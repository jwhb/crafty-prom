from prometheus_client import start_http_server
import yaml
import requests
import json
import time
import logging
from prometheus_client.registry import Collector
import os
from prometheus_client.core import GaugeMetricFamily, CounterMetricFamily, InfoMetricFamily, REGISTRY
from dateutil import parser
from datetime import datetime
import humanfriendly

crafty_api_timeout = 5


class CraftyInstance:
    def __init__(self, raw):
        self.hostname = raw['hostname']
        self.username = raw['username']
        self.password = raw['password']
        self.api_baseurl = f"https://{self.hostname}/api/v2"
        self.api_token = None

    def _get_api_token(self):
        if self.api_token is not None:
            return self.api_token
        logger.debug(f"authenticating to {self.api_baseurl}")
        response = requests.post(f"{self.api_baseurl}/auth/login", json={
                                 "username": self.username, "password": self.password}).json()
        self.api_token = response['data']['token']
        return self.api_token

    def _get_auth_header(self):
        return {'Authorization': 'Bearer ' + self._get_api_token()}

    def get_servers(self):
        response = requests.get(f"{self.api_baseurl}/servers",
                                headers=self._get_auth_header(), timeout=crafty_api_timeout).json()
        return response

    def get_server_stats(self, id):
        response = requests.get(f"{self.api_baseurl}/servers/{id}/stats",
                                headers=self._get_auth_header(), timeout=crafty_api_timeout).json()
        return response


class StatusAggregator:
    def __init__(self, raw):
        self.crafty_instances = list(
            map(lambda ci: CraftyInstance(ci), raw['crafty_instances']))
        self.last_status = None

    def init_from_config(filename):
        with open(filename) as stream:
            return StatusAggregator(yaml.safe_load(stream))

    def get_server_info(self, output_file="server_info.json"):
        servers_info = []
        for crafty in self.crafty_instances:
            try:
                servers = crafty.get_servers()
            except:
                logger.error(f"error fetching {crafty.hostname}")

            if servers['status'] != "ok":
                logger.error(f"non-ok response from {crafty.hostname}")
                pass
            for server in servers['data']:
                stats = crafty.get_server_stats(server['server_id'])
                if stats['status'] == 'ok':
                    if server['server_ip'] == '127.0.0.1':
                        stats['data']['hostname'] = crafty.hostname
                    servers_info.append(stats['data'])

        if output_file is not None:
            with open(output_file, 'w') as f:
                json.dump(servers_info, f)

        logger.debug("Finished update")
        self.last_status = servers_info
        return servers_info


class AppMetrics(Collector):
    def __init__(self, config_file, polling_interval_seconds=5):
        self.polling_interval_seconds = polling_interval_seconds

        self.status = StatusAggregator.init_from_config(config_file)

    def run_metrics_loop(self):
        while True:
            self.fetch()
            time.sleep(self.polling_interval_seconds)

    def fetch(self):
        self.status.get_server_info()

    def collect(self):
        if self.status.last_status is None:
            logger.warning("status not yet received")
            return

        # yield GaugeMetricFamily('my_gauge', 'Help text', value=7)
        crashed = GaugeMetricFamily(
            'crashed', 'Server has crashed', labels=['server_id'])
        cpu = GaugeMetricFamily('cpu_usage', 'Current CPU usage', labels=['server_id'])
        created = CounterMetricFamily(
            'created_seconds', 'Created seconds ago', labels=['server_id'])
        connection = InfoMetricFamily(
            'connection', 'Connection data', labels=['server_id'])
        players_online = GaugeMetricFamily('players_online', 'Players online', labels=['server_id'])
        players_max = GaugeMetricFamily('players_max', 'Max players count', labels=['server_id'])
        memory = GaugeMetricFamily('memory_usage_mb', 'Current memory usage in MB', labels=['server_id'])
        memory_percent = GaugeMetricFamily('memory_percent', 'Current memory usage percent', labels=['server_id'])
        running = GaugeMetricFamily('running', 'Server is running', labels=['server_id'])
        started = CounterMetricFamily(
            'started_seconds', 'Started seconds ago', labels=['server_id'])
        world_size = GaugeMetricFamily('world_size_mb', 'World size in MB', labels=['server_id'])

        for status in self.status.last_status:
            srv = status['server_id']
            id = srv['server_id']

            crashed.add_metric([id], int(status['crashed']))
            cpu.add_metric([id], status['cpu'])
            try:
              created.add_metric(
                [id], (datetime.now() - parser.parse(srv['created'])).total_seconds())
            except:
              logger.warning(f"Failed to parse created value {srv['created']}")
            connection.add_metric([id], {
                'hostname': status['hostname'] if 'hostname' in status else srv['server_ip'],
                'server_port': str(srv['server_port']),
                'description': status['desc'],
                'world_name': status['world_name'],
                'server_type': srv['type'],
                'version': status['version']
            })
            players_online.add_metric([id], status['online'])
            players_max.add_metric([id], status['max'])
            try:
              memory.add_metric([id], 0 if type(status['mem']) != str else humanfriendly.parse_size(status['mem'])/(1000*1000))
            except:
              logger.exception(f"Failed to parse memory value {status['mem']}")
            memory_percent.add_metric([id], status['mem_percent'])
            running.add_metric([id], int(status['running']))
            try:
              started.add_metric(
                [id], -1 if status['started'] == 'False' else (datetime.now() - parser.parse(status['started'])).total_seconds())
            except:
              logger.warning(f"Failed to parse started value {status['started']}")
            try:
              world_size.add_metric([id], humanfriendly.parse_size(status['world_size'])/(1000*1000)) # TODO needs conversion
            except:
              logger.warning(f"Failed to parse world size value {status['world_size']}")

        yield crashed
        yield cpu
        yield created
        yield connection
        yield players_online
        yield players_max
        yield memory
        yield memory_percent
        yield running
        yield started
        yield world_size


logger = logging.getLogger(__name__)


def main():
    logging.basicConfig(
        level=os.environ.get('LOGLEVEL', 'INFO').upper(), format='%(asctime)s.%(msecs)03d %(levelname)s {%(module)s} [%(funcName)s] %(message)s', datefmt='%Y-%m-%d,%H:%M:%S',)
    logger.info("Started the server info updater")

    config_file=os.getenv("CRAFTY_CONFIG", "config.yaml")
    polling_interval_seconds = int(os.getenv("POLLING_INTERVAL_SECONDS", "15"))
    exporter_port = int(os.getenv("EXPORTER_PORT", "9877"))
    crafty_api_timeout = int(os.getenv("CRAFTY_API_TIMEOUT", "5"))

    app_metrics = AppMetrics(
        config_file=config_file,
        polling_interval_seconds=polling_interval_seconds
    )
    REGISTRY.register(app_metrics)
    start_http_server(exporter_port)
    app_metrics.run_metrics_loop()


if __name__ == '__main__':
    main()
