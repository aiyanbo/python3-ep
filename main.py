#!/usr/bin/env python3

import yaml
from jinja2 import Environment, FileSystemLoader
import click


def _load_services(path):
    with open("services.yaml") as stream:
        services = yaml.full_load(stream)
    for service_name in services:
        service = services.get(service_name)
        service["hosts"] = ["localhost"]
        service["grpc"] = {"port": 18080}
        service["http"] = {"port": 8080}
        service["dubbo"] = {"port": 28080}
    return services


def _load_cdp_config(path):
    with open(path) as stream:
        return yaml.full_load(stream)


def _render_config(workdir, path, app_vars):
    print(f"Render config {path} in {workdir}")
    env = Environment(loader=FileSystemLoader(workdir))
    tpl = env.get_template(path)
    content = tpl.render(app_vars)
    print(content)


@click.group()
def cli():
    pass


@cli.command()
@click.option("-w", help="Working dir")
def template(w):
    if w is None:
        w = "/workspace"
    config = _load_cdp_config(f"{w}/cdp.yml")
    services = _load_services("")
    for entry in config.get("configs"):
        path = entry.get("path")
        global_vars = {"hashids_salt": "123"}
        app_vars = {"app_deploy_dir": "/workspace", "services": services, "global": global_vars,
                    "resources": {
                        "postgresql": {
                            "cdp": {
                                "host": "localhost"
                            }
                        },
                        "redis": {
                            "graphql_gateway": {
                                "host": "localhost"
                            }
                        }
                    },
                    "custom_configs": {
                        "graphql_gateway": {
                            "access_limit": 100,
                            "auth_switch": "True"
                        }
                    }}
        # appvars["custom_configs"] = config["custom_configs"]
        _render_config(w, path, app_vars)


if __name__ == "__main__":
    cli()
