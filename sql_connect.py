import sqlite3

class Database:
    def __init__(self, database, table):
        self.db = sqlite3.connect(database)
        self.db_name = table
        self.cur = self.db.cursor()

    def insert(self, values: dict):
        value = []
        for i in values.values():
            if type(i) == str:
                value.append(f"'{i}'")
            else:
                value.append(f"{i}")
        keys = list(values.keys())
        self.cur.execute(f'''
            insert into {self.db_name}({','.join(keys)}) values({",".join(value)})
        ''')
        self.db.commit()

    def update(self, values:dict, wheres:dict):
        changes = []
        wherelist = []
        for key in values:
            if type(values[key]) == str:
                changes.append(f"{key} = '{values[key]}'")
            else:
                changes.append(f"{key} = {values[key]}")
        for key in wheres:
            if type(wheres[key]) == str:
                wherelist.append(f"{key} = '{wheres[key]}'")
            else:
                wherelist.append(f"{key} = {wheres[key]}")
        self.cur.execute(f'''
            update {self.db_name} set {",".join(changes)} where {",".join(wherelist)}
        ''')
        self.db.commit()

    def delete(self, wheres:dict):
        wherelist = []
        for key in wheres:
            if type(wheres[key]) == str:
                wherelist.append(f"{key} = '{wheres[key]}'")
            else:
                wherelist.append(f"{key} = {wheres[key]}")
        self.cur.execute(f'''
                    delete from {self.db_name} where {",".join(wherelist)}
                ''')
        self.db.commit()

    def select(self, wheres:dict):
        wherelist = []
        for key in wheres:
            if type(wheres[key]) == str:
                wherelist.append(f"{key} = '{wheres[key]}'")
            else:
                wherelist.append(f"{key} = {wheres[key]}")
        self.cur.execute(f'''
                            select * from {self.db_name} where {",".join(wherelist)}
                        ''')
        return self.cur.fetchall()

