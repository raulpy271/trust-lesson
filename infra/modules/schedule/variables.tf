
variable "stage" {
  type = string
}

variable "rg_name" {
  type = string
}

variable "rg_location" {
  type = string
}

variable "storage_account_name" {
  type = string
}

variable "storage_access_key" {
  type = string
}

variable "app_envs" {
  type = map(string)
}
