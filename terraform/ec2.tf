resource "aws_instance" "notebook_server" {
  # 4 cpu, 8gb memory, no nvme (have to attach block store separately)
  instance_type = "c6g.xlarge"
  ami           = "ami-03b5637245555e13d"

  key_name                    = aws_key_pair.notebook_server_key_pair.key_name
  associate_public_ip_address = true
  availability_zone           = "us-east-1a"
  count                       = var.instance_count

  tags = {
    Name = "Notebook server"
  }
}

resource "aws_key_pair" "notebook_server_key_pair" {
  public_key = var.notebook_server_public_key
  key_name   = "foss4g_notebook_server_key"
}

resource "aws_ebs_volume" "data_volume" {
  size              = 128
  availability_zone = "us-east-1a"
  count             = var.instance_count
}

resource "aws_volume_attachment" "data_volume_attachment" {
  device_name = "/dev/sdh"
  for_each    = { for idx in range(var.instance_count) : idx => tostring(idx) }
  volume_id   = aws_ebs_volume.data_volume[each.key].id
  instance_id = aws_instance.notebook_server[each.key].id
}

output "instance_ips" {
  value = aws_instance.notebook_server.*.public_ip
}