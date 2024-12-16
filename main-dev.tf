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
  command = ["sleep", "infinity"]
  ports {
    internal = 80
    external = 8000
  }
  volumes {
    host_path = abspath("api/")
    container_path = "/api/"
  }
}
