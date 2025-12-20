
variable "stage" {
  type = string
}

variable "rg_name" {
  type = string
}

variable "rg_location" {
  type = string
}

variable "app_envs" {
  type = map(string)
}

variable "insights_instrumentation_key" {
  type = string
}

variable "storage_lesson_image_id" {
  type = string
}

variable "storage_lesson_spreadsheet_id" {
  type = string
}
