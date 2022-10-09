import ...configs

config = configs.config_parser()

print(config.setup_config_parser("configs/setup.cfg"))
print(config.permission_config_parser("configs/permissions.cfg"))
