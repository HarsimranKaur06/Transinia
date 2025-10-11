# Only standard availability zones (exclude Local Zones / Wavelength)
data "aws_availability_zones" "standard" {
  state = "available"

  # Standard AZs don't require opt-in
  filter {
    name   = "opt-in-status"
    values = ["opt-in-not-required"]
  }

  # Ensure we don't pick Local Zones
  filter {
    name   = "zone-type"
    values = ["availability-zone"]
  }
}

locals {
  azs_std       = slice(data.aws_availability_zones.standard.names, 0, 2) # pick first two standard AZs
  public_cidrs  = var.public_subnet_cidrs
  private_cidrs = var.private_subnet_cidrs
}

resource "aws_vpc" "main" {
  count = var.create_vpc_resources ? 1 : 0
  
  cidr_block = var.vpc_cidr
  tags       = merge(local.tags, { Name = "${local.app}-${local.env}-vpc" })
}

# Data source to fetch existing VPC if not creating one
data "aws_vpc" "existing" {
  count = (!var.create_vpc_resources && var.use_existing_vpc_resources) ? 1 : 0
  
  filter {
    name   = "tag:Name"
    values = ["${local.app}-${local.env}-vpc"]
  }
}

# Local value to use either the created VPC or the data source
locals {
  # Default VPC ID fallback (replace with actual ID from your environment)
  vpc_id_default = "vpc-default"
  
  # Use created resources, existing resources, or fallbacks
  vpc_id = var.create_vpc_resources ? aws_vpc.main[0].id : (
    var.use_existing_vpc_resources ? data.aws_vpc.existing[0].id : local.vpc_id_default
  )
}

resource "aws_internet_gateway" "igw" {
  count = var.create_vpc_resources ? 1 : 0
  
  vpc_id = local.vpc_id
  tags   = merge(local.tags, { Name = "${local.app}-${local.env}-igw" })
}

# PUBLIC SUBNETS (2) — pinned to first two standard AZs
resource "aws_subnet" "public_a" {
  count = var.create_vpc_resources ? 1 : 0
  
  vpc_id                  = local.vpc_id
  cidr_block              = local.public_cidrs[0]
  availability_zone       = local.azs_std[0]
  map_public_ip_on_launch = true
  tags                    = merge(local.tags, { Name = "${local.app}-${local.env}-subnet-public-a" })
}

resource "aws_subnet" "public_b" {
  count = var.create_vpc_resources ? 1 : 0
  
  vpc_id                  = local.vpc_id
  cidr_block              = local.public_cidrs[1]
  availability_zone       = local.azs_std[1]
  map_public_ip_on_launch = true
  tags                    = merge(local.tags, { Name = "${local.app}-${local.env}-subnet-public-b" })
}

# Add variable to control data sources for VPC resources
variable "use_existing_vpc_resources" {
  type        = bool
  default     = false
  description = "Whether to use data sources to lookup existing VPC resources"
}

# Data sources to fetch existing subnets if not creating them
data "aws_subnet" "public_a" {
  count = var.use_existing_vpc_resources ? 1 : 0
  
  filter {
    name   = "tag:Name"
    values = ["${local.app}-${local.env}-subnet-public-a"]
  }
  
  # Add depends_on to make this more stable and avoid failures during first apply
  depends_on = [
    data.aws_vpc.existing
  ]
}

data "aws_subnet" "public_b" {
  count = var.use_existing_vpc_resources ? 1 : 0
  
  filter {
    name   = "tag:Name"
    values = ["${local.app}-${local.env}-subnet-public-b"]
  }
  
  # Add depends_on to make this more stable and avoid failures during first apply
  depends_on = [
    data.aws_vpc.existing
  ]
}

# Local values for subnet IDs
locals {
  # Default fallback IDs if needed (these can be actual IDs from your environment)
  public_subnet_a_id_default = "subnet-default-a"
  public_subnet_b_id_default = "subnet-default-b"
  
  # Use created resources, existing resources, or fallbacks
  public_subnet_a_id = var.create_vpc_resources ? aws_subnet.public_a[0].id : (
    var.use_existing_vpc_resources ? data.aws_subnet.public_a[0].id : local.public_subnet_a_id_default
  )
  
  public_subnet_b_id = var.create_vpc_resources ? aws_subnet.public_b[0].id : (
    var.use_existing_vpc_resources ? data.aws_subnet.public_b[0].id : local.public_subnet_b_id_default
  )
}

resource "aws_route_table" "public" {
  count = var.create_vpc_resources ? 1 : 0
  
  vpc_id = local.vpc_id
  tags   = merge(local.tags, { Name = "${local.app}-${local.env}-rt-public" })
}

data "aws_route_table" "public" {
  count = (!var.create_vpc_resources && var.use_existing_vpc_resources) ? 1 : 0
  
  filter {
    name   = "tag:Name"
    values = ["${local.app}-${local.env}-rt-public"]
  }
}

locals {
  # Default route table ID fallback
  public_route_table_id_default = "rtb-default-public"
  
  # Use created resources, existing resources, or fallbacks
  public_route_table_id = var.create_vpc_resources ? aws_route_table.public[0].id : (
    var.use_existing_vpc_resources ? data.aws_route_table.public[0].id : local.public_route_table_id_default
  )
}

resource "aws_route" "public_igw" {
  count = var.create_vpc_resources ? 1 : 0
  
  route_table_id         = local.public_route_table_id
  destination_cidr_block = "0.0.0.0/0"
  gateway_id             = var.create_vpc_resources ? aws_internet_gateway.igw[0].id : null
}

resource "aws_route_table_association" "public_assoc_a" {
  count = var.create_vpc_resources ? 1 : 0
  
  subnet_id      = local.public_subnet_a_id
  route_table_id = local.public_route_table_id
}

resource "aws_route_table_association" "public_assoc_b" {
  count = var.create_vpc_resources ? 1 : 0
  
  subnet_id      = local.public_subnet_b_id
  route_table_id = local.public_route_table_id
}

# NAT for private subnets — place NAT GW in a STANDARD AZ public subnet
resource "aws_eip" "nat" {
  count = var.create_vpc_resources ? 1 : 0
  
  domain     = "vpc"
  depends_on = [aws_internet_gateway.igw]
  tags       = merge(local.tags, { Name = "${local.app}-${local.env}-nat-eip" })
}

resource "aws_nat_gateway" "nat" {
  count = var.create_vpc_resources ? 1 : 0
  
  allocation_id = aws_eip.nat[0].id
  subnet_id     = local.public_subnet_a_id
  tags          = merge(local.tags, { Name = "${local.app}-${local.env}-nat" })
}

# PRIVATE SUBNETS (2) — pinned to the same two standard AZs
resource "aws_subnet" "private_a" {
  count = var.create_vpc_resources ? 1 : 0
  
  vpc_id            = local.vpc_id
  cidr_block        = local.private_cidrs[0]
  availability_zone = local.azs_std[0]
  tags              = merge(local.tags, { Name = "${local.app}-${local.env}-private-1" })
}

resource "aws_subnet" "private_b" {
  count = var.create_vpc_resources ? 1 : 0
  
  vpc_id            = local.vpc_id
  cidr_block        = local.private_cidrs[1]
  availability_zone = local.azs_std[1]
  tags              = merge(local.tags, { Name = "${local.app}-${local.env}-private-2" })
}

# Data sources to fetch existing private subnets if not creating them
data "aws_subnet" "private_a" {
  count = (!var.create_vpc_resources && var.use_existing_vpc_resources) ? 1 : 0
  
  filter {
    name   = "tag:Name"
    values = ["${local.app}-${local.env}-private-1"]
  }
}

data "aws_subnet" "private_b" {
  count = (!var.create_vpc_resources && var.use_existing_vpc_resources) ? 1 : 0
  
  filter {
    name   = "tag:Name"
    values = ["${local.app}-${local.env}-private-2"]
  }
}

# Local values for private subnet IDs
locals {
  # Default private subnet IDs (replace with actual IDs from your environment)
  private_subnet_a_id_default = "subnet-default-private-a"
  private_subnet_b_id_default = "subnet-default-private-b"
  
  # Use created resources, existing resources, or fallbacks
  private_subnet_a_id = var.create_vpc_resources ? aws_subnet.private_a[0].id : (
    var.use_existing_vpc_resources ? data.aws_subnet.private_a[0].id : local.private_subnet_a_id_default
  )
  
  private_subnet_b_id = var.create_vpc_resources ? aws_subnet.private_b[0].id : (
    var.use_existing_vpc_resources ? data.aws_subnet.private_b[0].id : local.private_subnet_b_id_default
  )
  
  private_subnet_ids  = [local.private_subnet_a_id, local.private_subnet_b_id]
}

resource "aws_route_table" "private" {
  count = var.create_vpc_resources ? 1 : 0
  
  vpc_id = local.vpc_id
  tags   = merge(local.tags, { Name = "${local.app}-${local.env}-private-rt" })
}

# Data source for existing private route table
data "aws_route_table" "private" {
  count = (!var.create_vpc_resources && var.use_existing_vpc_resources) ? 1 : 0
  
  filter {
    name   = "tag:Name"
    values = ["${local.app}-${local.env}-private-rt"]
  }
}

# Local value for private route table ID
locals {
  # Default private route table ID fallback
  private_route_table_id_default = "rtb-default-private"
  
  # Use created resources, existing resources, or fallbacks
  private_route_table_id = var.create_vpc_resources ? aws_route_table.private[0].id : (
    var.use_existing_vpc_resources ? data.aws_route_table.private[0].id : local.private_route_table_id_default
  )
}

resource "aws_route" "private_nat" {
  count = var.create_vpc_resources ? 1 : 0
  
  route_table_id         = local.private_route_table_id
  destination_cidr_block = "0.0.0.0/0"
  nat_gateway_id         = aws_nat_gateway.nat[0].id
}

resource "aws_route_table_association" "private_assoc_a" {
  count = var.create_vpc_resources ? 1 : 0
  
  subnet_id      = local.private_subnet_a_id
  route_table_id = local.private_route_table_id
}

resource "aws_route_table_association" "private_assoc_b" {
  count = var.create_vpc_resources ? 1 : 0
  
  subnet_id      = local.private_subnet_b_id
  route_table_id = local.private_route_table_id
}
