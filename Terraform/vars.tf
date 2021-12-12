variable "AWS_ACCESS_KEY" {
}

variable "AWS_SECRET_KEY" {
}

variable "AWS_REGION" {
  default = "us-east-1"
}

variable "VPC_ID" {
  default = "vpc-52565a28"
}

variable "AMIS" {
  type = map(string)
  default = {
    us-east-1 = "ami-0e472ba40eb589f49"
  }
}

variable "PATH_TO_PRIVATE_KEY" {
}

variable "PATH_TO_PUBLIC_KEY" {
}

variable "INSTANCE_USERNAME" {
  default = "ubuntu"
}
