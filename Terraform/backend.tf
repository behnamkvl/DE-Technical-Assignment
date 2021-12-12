terraform {
 backend "s3" {
   bucket = "behnam-test-bestsellers"
   key    = "terraform/terraform.tfstate"
   region = "us-east-1"
 }
}
