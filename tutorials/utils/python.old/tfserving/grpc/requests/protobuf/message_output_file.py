def gen_output_file(message, output_file=None):
    output_menu  = "Pick an output format:\n"
    output_menu += "\t0. Do nothing (message will be discarded!)\n"
    output_menu += "\t1. text-format\n"
    output_menu += "\t2. json-format\n"
    output_menu += "Choose: "

    answer = int( input(output_menu) )
    if answer == 1:
        from google.protobuf import text_format
        print("> text-format chosen.")

        if output_file:
            name = output_file
        else:
            name = input("Pick a name for output file: ")
            add_ext = input("Add \'.txt\' to name? (y/n): ")
            if add_ext != 'n':
                name += '.txt'

        print(f"Saving text-format protobuf in {name}")
        with open(name, 'w') as textformat_file:
            text_format.PrintMessage(message, textformat_file)

    if answer == 2:
        import json
        from google.protobuf import json_format
        print("> json-format chosen.")

        answer = input("Add customized pairs to JSON? (y/n): ")
        if answer != 'n':
            output_dict = {}

            message_key = input("Set key string for message: ")
            output_dict[message_key] = json_format.MessageToDict(message)

            answer = input("Add another key-value pair? (y/n): ")
            while answer != 'n':
                key = input("Set key: ")
                value_str = input("Set value: ")
                value = json.loads( value_str )

                output_dict[key] = value

                answer = input("Add another key-value pair? (y/n): ")
        else:
            output_dict = json_format.MessageToDict(message)

        if output_file:
            name = output_file
        else:
            name = input("Pick a name for output file: ")
            add_ext = input("Add \'.json\' to name? (y/n): ")
            if add_ext != 'n':
                name += '.json'
        
        print(f"Saving json-format protobuf in {name}")
        with open(name, 'w') as jsonformat_file:
            json.dump(output_dict, jsonformat_file, indent=2)