import argparse
import glob
import json
import os
import textwrap
from datetime import datetime
import pandas as pd
import networkx as nx
import xml.etree.ElementTree as ET

class MIPTableViewer:
    def __init__(self, tables_directory=None, prefix=None, output_directory=None):
        self.tables_directory = tables_directory
        self.prefix = prefix
        self.output_directory = output_directory

    def get_mip_tables(self):
        glob_string = os.path.join(self.tables_directory, '{}_*.json'.format(self.prefix))
        mip_table_json = glob.glob(glob_string)
        tables_with_variables = {}
        excluded_tables = ['grids', 'formula_terms', 'coordinate', 'CV']

        for table_path in mip_table_json:
            table_name = os.path.basename(table_path).split('_')[1].split('.json')[0]
            with open(table_path, 'r') as f:
                table_json = json.load(f)

            if "variable_entry" in table_json and table_name not in excluded_tables:
                tables_with_variables[table_name] = table_path

        return tables_with_variables

    def extract_table_data(self, tables):
        table_data = []
        for table, table_path in tables.items():
            with open(table_path, 'r') as f:
                variable_entry = json.load(f).get("variable_entry", {})
            for variable, metadata in variable_entry.items():
                table_data.append(
                    [table, variable, metadata.get('frequency', ''), metadata.get('dimensions', ''),
                     metadata.get('standard_name', ''), metadata.get('long_name', ''),
                     metadata.get('comment', ''), metadata.get('modeling_realm', ''),
                     metadata.get('units', ''), metadata.get('positive', ''),
                     metadata.get('cell_methods', ''), metadata.get('cell_measures', '')])

        return table_data

    def wrap_text(self, input_text, wrap_size):
        if len(input_text) > wrap_size:
            wrapped_input_text = textwrap.wrap(input_text, width=wrap_size, break_long_words=True)
            wrapped_input_text = "\n".join(wrapped_input_text)
            return wrapped_input_text
        else:
            return input_text

    def create_dataframe(self, table_data):
        headings = ['Table', 'Variable', 'Frequency', 'Dimensions', 'Standard Name', 'Long Name',
                    'Comment', 'Modeling Realm', 'Units', 'Positive', 'Cell Methods', 'Cell Measures']
        df = pd.DataFrame(table_data, columns=headings)
        return df

    def create_graph(self, table_data):
        G = nx.Graph()

        for row in table_data:
            table = row[0]
            variable = row[1]
            modeling_realm = row[7]
            metadata = row[2:]

            G.add_node(table, type='table')
            G.add_node(variable, type='variable', metadata=dict(zip(['Frequency', 'Dimensions', 'Standard Name', 'Long Name',
                                                                    'Comment', 'Modeling Realm', 'Units', 'Positive',
                                                                    'Cell Methods', 'Cell Measures'], metadata)))
            G.add_node(modeling_realm, type='modeling_realm')

            G.add_edge(table, variable)
            G.add_edge(variable, modeling_realm)

        return G


    def output_to_graphx(self):
        tables = self.get_mip_tables()
        table_data = self.extract_table_data(tables)
        G = self.create_graph(table_data)
        return G

    def save_gexf_file(self, G, filepath):
        root = ET.Element('gexf', xmlns='http://www.gexf.net/1.3', version='1.3')
        graph = ET.SubElement(root, 'graph', mode='static', defaultedgetype='directed')

        # Add attributes
        attributes = G.nodes(data='metadata')
        attributes = list(attributes)
        attribute_names = list(attributes[0][1].keys())

        attributes_element = ET.SubElement(graph, 'attributes', mode='static')

        for i, attr_name in enumerate(attribute_names):
            ET.SubElement(attributes_element, 'attribute', {'id': str(i), 'title': attr_name, 'type': 'string'})

        for node, attributes in G.nodes(data=True):
            node_id = node.replace(' ', '_')
            node_label = node
            node_element = ET.SubElement(graph, 'node', id=node_id, label=node_label)

            if 'metadata' in attributes:
                metadata = attributes['metadata']
                attvalues_element = ET.SubElement(node_element, 'attvalues')

                for i, attr_name in enumerate(attribute_names):
                    attr_value = metadata.get(attr_name, 'none')
                    ET.SubElement(attvalues_element, 'attvalue', {'for': str(i), 'value': str(attr_value)})

        for source, target in G.edges():
            source_id = source.replace(' ', '_')
            target_id = target.replace(' ', '_')
            ET.SubElement(graph, 'edge', source=source_id, target=target_id)

        tree = ET.ElementTree(root)
        tree.write(filepath, encoding='utf-8', xml_declaration=True)

    def output(self, kind='html'):
        output_filepath = os.path.join(self.output_directory, f'mip_table_viewer_{self.prefix}.{kind}')
        if kind == 'csv':
            df = self.output_to_dataframe()
            self.save_dataframe(df, output_filepath)
        elif kind == 'gexf':
            G = self.output_to_graphx()
            self.save_gexf_file(G, output_filepath)
        else:
            html = self.output_to_html()
            self.save_html(html, output_filepath)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--tables_directory', help='Directory of the mip tables to generate an HTML page for.', type=str, required=False)
    parser.add_argument('-p', '--prefix', help='Prefix used on the mip table JSON files.', type=str, required=False)
    parser.add_argument('-o', '--output_directory', help='Output location of the generated HTML page.', type=str, required=False)
    args = parser.parse_args()

    tables_directory = args.tables_directory or '../Tables'
    prefix = args.prefix or 'ARISE'
    output_directory = args.output_directory or './'

    mip_table_viewer = MIPTableViewer(tables_directory, prefix, output_directory)
    mip_table_viewer.output('gexf')
