#!/usr/bin/env python3
from fire import Fire

from launch import teardown_docker_compose

if __name__ == "__main__":
    Fire(teardown_docker_compose)
