resource "aws_instance" "notebook_server" {
  # Ubuntu 20.04, 2021-08-25
  ami = "ami-03b5637245555e13d"
  # 4 cpu, 8gb memory, decent sized ssd
  instance_type = "c6gd.xlarge"

  key_name                    = aws_key_pair.notebook_server_key_pair.key_name
  associate_public_ip_address = true
  count                       = var.instance_count

  # vpc_security_group_ids = [aws_security_group.notebook_server_sg.id]
  # subnet_id              = aws_subnet.notebook_server_subnet.id

  tags = {
    Name = "Notebook server"
  }
}

resource "aws_key_pair" "notebook_server_key_pair" {
  public_key = var.notebook_server_public_key
  key_name   = "foss4g_notebook_server_key"
}

resource "aws_vpc" "notebook_server_vpc" {
  cidr_block = "10.0.0.0/16"
}

# The notebook server needs to accept ssh connections on the standard
# port (for configuration) and TCP connections on :8888 for notebook
# connections
# It needs to allow outbound access to the Raster Foundry API and
# I think nothing else
resource "aws_security_group" "notebook_server_sg" {
  vpc_id = aws_vpc.notebook_server_vpc.id
}

resource "aws_security_group_rule" "notebook_server_ssh" {
  type             = "ingress"
  from_port        = 22
  to_port          = 22
  protocol         = "tcp"
  cidr_blocks      = ["0.0.0.0/0"]
  ipv6_cidr_blocks = ["::/0"]

  security_group_id = aws_security_group.notebook_server_sg.id
}

resource "aws_security_group_rule" "notebook_server_jupyter_8888" {
  type             = "ingress"
  from_port        = 8888
  to_port          = 8888
  protocol         = "tcp"
  cidr_blocks      = ["0.0.0.0/0"]
  ipv6_cidr_blocks = ["::/0"]

  security_group_id = aws_security_group.notebook_server_sg.id
}

resource "aws_subnet" "notebook_server_subnet" {
  vpc_id            = aws_vpc.notebook_server_vpc.id
  cidr_block        = "10.0.10.0/24"
  availability_zone = "us-east-1a"
}

output "instance_ips" {
  value = aws_instance.notebook_server.*.ipv6_address_count
}

output "security_group_id" {
  value = aws_security_group.notebook_server_sg.id
}