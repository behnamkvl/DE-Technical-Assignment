data "aws_ip_ranges" "bestsellers_ec2" {
  regions  = ["us-east-1"]
  services = ["ec2"]
}

resource "aws_security_group" "bestsellers_security_group" {
  name          = "bestsellers_security_group"
  vpc_id        = var.VPC_ID

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  # Allow outbound internet access.
  egress {
    from_port   = 8080
    to_port     = 8080
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "bestsellers_security_group"
    CreateDate  = data.aws_ip_ranges.bestsellers_ec2.create_date
    SyncToken   = data.aws_ip_ranges.bestsellers_ec2.sync_token
  }
}

