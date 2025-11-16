terraform {
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.6.2"
    }
  }
}

provider "docker" {}

locals {
  db_url = "postgresql+psycopg://${var.db_user}:${var.db_password}@localhost:${var.db_port_ext}/${var.db_name}"
}

resource "docker_image" "api-img" {
  name = "api-img"
  build {
    context = "api/"
    dockerfile = "Dockerfile-dev"
  }
}

resource "docker_container" "api" {
  image = docker_image.api-img.image_id
  name  = "api"
  ports {
    internal = 8000
    external = 8000
  }
  volumes {
    host_path = abspath("api/")
    container_path = "/api/"
  }
  env = [
    "REDIS_HOST=${docker_container.redis.hostname}",
    "REDIS_PASSWORD=${var.redis_password}",
    "DB_HOST=${docker_container.postgres.hostname}",
    "DB_USER=${var.db_user}",
    "DB_PASSWORD=${var.db_password}",
    "DB_NAME=${var.db_name}",
    "DB_PORT=${var.db_port}",
    "STORAGE_URL=${var.storage_url}"
    #"DB_DIALECT=sqlite",
    #"DB_DRIVER=pysqlite",
  ]
  networks_advanced {
    name = docker_network.api_network.id
  }
}

resource "docker_container" "redis" {
  image = "redis:7.2.4-alpine3.19"
  name = "redis"
  hostname = "redis"
  command = ["redis-server", "--requirepass", var.redis_password]
  networks_advanced {
    name = docker_network.api_network.id
  }
}

resource "docker_container" "postgres" {
  image = "postgres:17.1-alpine3.20"
  name = "postgres"
  hostname = "postgres"
  env = [
    "POSTGRES_USER=${var.db_user}",
    "POSTGRES_PASSWORD=${var.db_password}",
    "POSTGRES_DB=${var.db_name}"
  ]
  networks_advanced {
    name = docker_network.api_network.id
  }
  volumes {
    volume_name = "pgdata"
    container_path = "/var/lib/postgresql/data"
  }
  ports {
    internal = var.db_port
    external = var.db_port_ext
  }
  provisioner "local-exec" {
    command = "poetry -P api run alembic -x sqlalchemy.url=${local.db_url} upgrade head"
  }
}

resource "docker_network" "api_network" {
  name = "api_network"
}
