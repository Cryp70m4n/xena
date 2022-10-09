tests_passed = 0
total_tests = 0


class tests():
    def auth_module_test():
        from auth import authorisation

        auth = authorisation()

        if auth.throw_success("Test successful!") != True:
            return "[X] - Auth module test failed!"
        return True

    def config_module_test():
        import configs

        config = configs.config_parser()

        if type(config.setup_config_parser("configs/setup.cfg")) is not dict:
            return "[X] - Setup config test failed!"
        if type(config.permission_config_parser("configs/permissions.cfg")) is not dict:
            return "[X] - Permission config test failed!"
        return True


tests_list = dir(tests)
for test in tests_list:
    if test.startswith('__') != True:
        total_tests+=1


auth_module_test_output = tests.auth_module_test()
config_module_test_output = tests.config_module_test()

if auth_module_test_output != True:
    print(auth_module_test_output)
    print("Auth module test failed")
else:
    tests_passed+=1

if config_module_test_output != True:
    print(config_module_test_output)
    print("Config module test failed")
else:
    tests_passed+=1

print(f"[!] Total tests passed:{tests_passed}/{total_tests}")