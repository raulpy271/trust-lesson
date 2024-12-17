terraform {
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.0.1"
    }
  }
}

provider "docker" {}

resource "docker_image" "api-img" {
  name = "api-img"
  build {
    context = "api/"
  }
}

resource "docker_container" "api" {
  image = docker_image.api-img.image_id
  name  = "api"
  ports {
    internal = 5000
    external = 5000
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
    "DB_NAME=${var.db_name}"
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
}

resource "docker_network" "api_network" {
  name = "api_network"
}
