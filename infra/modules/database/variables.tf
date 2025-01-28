
variable "db_user" {
  default = "apiuser"
}

variable "db_name" {
  default = "api"
}

variable "stage" {
  type = string
}

variable "rg_name" {
  type = string
}

variable "rg_location" {
  type = string
}
