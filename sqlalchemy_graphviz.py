"""Generate a dot file from a SQLAlchemy metadata schema.

Requires BeautifulSoup and pydot.

"""
from pydot import Dot, Node, Edge
from bs4 import BeautifulSoup

def generate_dot_from_schema(metadata, name=None):
    graph = Dot(
        name or 'Database schema',
        splines='true',
        rankdir='LR',
    )

    graph.add_node(Node(
        'Description',
        shape='box',
        label=('<'
            'PK: Primary key<br />'
            'FK: Foreign key<br />'
            'UQ: Unique constraint<br />'
        '>'),
    ))


    for table_name, table in metadata.tables.items():
        soup = BeautifulSoup(f'''
            <table border="0" cellspacing="0" cellborder="1">
                <tr>
                    <td colspan="3" bgcolor="lightblue">
                        <font>{table_name}</font>
                    </td>
                </tr>
            </table>
        ''', 'html.parser')

        for column_name, column in table.columns.items():
            special = set()
            if column.unique:
                special.add('UQ')
            if column.primary_key:
                special.add('PK')
            if column.index:
                special.add('IX')
            if column.foreign_keys:
                special.add('FK')

            row_soup = BeautifulSoup(f'''
                <tr>
                    <td port="{column_name}_in">
                        <font>{','.join(special) if special else ' '}</font>
                    </td>
                    <td>
                        <font>{column_name}</font>
                    </td>
                    <td port="{column_name}_out">
                        <font>{str(column.type)}{'*' if column.nullable else ''}</font>
                    </td>
                </tr>
            ''', 'html.parser')
            soup.table.append(row_soup.tr)

            # Add edges
            for fk in column.foreign_keys:
                edge = Edge(
                    f'{table_name}:{column_name}_out:e',
                    f'{fk.column.table.name}:{fk.column.name}_in:w',
                )
                graph.add_edge(edge)

        node = Node(
            table_name,
            label=f'<{str(soup.table)}>',
            shape='none',
            dir='back',
            arrowhead='dot',
            arrowtail='crow',
        )

        graph.add_node(node)

    return graph


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'object',
        help='module path and attribute path separated by :, e.g app.db:Base.metadata')
    args = parser.parse_args()

    module_path, attributes = args.object.split(':')
    attributes = attributes.split('.')
    module = __import__(module_path)
    attribute = getattr(module, attributes[0])
    for attr in attributes[1:]:
        attribute = getattr(attribute, attr)

    print(generate_dot_from_schema(attribute, args.object).to_string())

if __name__ == '__main__':
    main()
