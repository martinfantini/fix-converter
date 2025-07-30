import unittest
from generator import *

class Testing_Generator(unittest.TestCase):

    def test_generator_data_definition(self):
        data_type = DataType( 
            name = "Test_Name",
            basic_type = "Test_Type",
            numeric_id = '8',
            primitive_size = '10',
            description = "Test_Description",
            min_value = '15',
            max_value = '20',
            range = "123-125",
            no_value = "0xFF00",
        )

        result = GeneratorBase.make_data_definition(data_type)

        self.assertEqual(result['token'], 'data')
        self.assertEqual(result['name'], "Test_Name")
        self.assertEqual(result['type'], "Test_Type")
        self.assertEqual(result['numeric_id'], '8')
        self.assertEqual(result['size'], '10')
        self.assertEqual(result['description'], "Test_Description")
        self.assertEqual(result['min_value'], '15')
        self.assertEqual(result['max_value'], '20')
        self.assertEqual(result['range'], "123-125")
        self.assertEqual(result['token'], 'data')
        self.assertEqual(result['no_value'], "0xFF00")

    def test_generator_data_enum_definition(self):
        data_type = DataType( 
            name = "Test_Name",
            basic_type = "Test_Type",
            numeric_id = '8',
            primitive_size = '10',
            description = "Test_Description",
            min_value = '15',
            max_value = '20',
            range = "123-125",
            no_value = "0xFF00",
        )


    @staticmethod
    def make_enum_definition(data_type: DataType) -> dict:
        valid_values = []
        if data_type.has_valid_values:
            for enum_element in data_type.valid_value_by_name.values():
                valid_values.append({
                    'name', enum_element.name,
                    'value', enum_element.value,
                    'description', enum_element.description,
                })

        return {
            'token': 'enum',
            'name': data_type.name,
            'type': data_type.basic_type,
            'numeric_id': data_type.numeric_id,
            'size': data_type.primitive_size,
            'description': data_type.description,
            'min_value': data_type.min_value,
            'max_value': data_type.max_value,
            'max_value': data_type.range,
            'no_value': data_type.no_value,
            'valid_values': valid_values,
        }