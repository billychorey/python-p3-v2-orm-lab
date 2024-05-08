from __init__ import CURSOR, CONN
from department import Department
from employee import Employee


class Review:
    # Dictionary of objects saved to the database.
    all = {}

    def __init__(self, year, summary, employee_id, id=None):
        self.id = id
        self.year = year  # This will invoke the year setter property
        self.summary = summary  # This will invoke the summary setter property
        self.employee_id = employee_id  # This will invoke the employee_id setter property

    @property
    def year(self):
        return self._year

    @year.setter
    def year(self, value):
        if not isinstance(value, int):
            raise ValueError("Year must be an integer")
        if value < 2000:
            raise ValueError("Year must be >= 2000")
        self._year = value

    @property
    def summary(self):
        return self._summary

    @summary.setter
    def summary(self, value):
        if not isinstance(value, str) or not value:
            raise ValueError("Summary must be a non-empty string")
        self._summary = value

    @property
    def employee_id(self):
        return self._employee_id
    
    @employee_id.setter
    def employee_id(self, value):
        if not isinstance(value, int):
            raise ValueError("Employee ID must be an integer")
        
        # Here, add a check to see if the employee exists in the database.
        if not Employee.find_by_id(value):
            raise ValueError("Employee ID must reference an existing employee in the database")
        
        self._employee_id = value

    def __repr__(self):
        return (
            f"<Review {self.id}: {self.year}, {self.summary}, "
            + f"Employee: {self.employee_id}>"
        )

    @classmethod
    def create_table(cls):
        """ Create a new table to persist the attributes of Review instances """
        sql = """
            CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY,
            year INT,
            summary TEXT,
            employee_id INTEGER,
            FOREIGN KEY (employee_id) REFERENCES employee(id))
        """
        CURSOR.execute(sql)
        CONN.commit()

    @classmethod
    def drop_table(cls):
        """ Drop the table that persists Review  instances """
        sql = """
            DROP TABLE IF EXISTS reviews;
        """
        CURSOR.execute(sql)
        CONN.commit()

    def save(self):
        if self.id is None:
            sql = "INSERT INTO reviews (year, summary, employee_id) VALUES (?, ?, ?)"
            CURSOR.execute(sql, (self.year, self.summary, self.employee_id))
            CONN.commit()
            self.id = CURSOR.lastrowid
        else:
            sql = "UPDATE reviews SET year = ?, summary = ?, employee_id = ? WHERE id = ?"
            CURSOR.execute(sql, (self.year, self.summary, self.employee_id, self.id))
            CONN.commit()
        Review.all[self.id] = self


    @classmethod
    def create(cls, year, summary, employee_id):
        review = cls(year, summary, employee_id)
        review.save()
        return review
   
    @classmethod
    def instance_from_db(cls, row):
       id, year, summary, employee_id = row
       if id in cls.all:
           review = cls.all[id]
           review.year = year  # Ensure correct year is always assigned
           review.summary = summary  # Ensure correct summary is always assigned
           review.employee_id = employee_id  # Ensure correct employee_id is always assigned
       else:
           review = cls(year, summary, employee_id, id)
           cls.all[id] = review
       return review
   

    @classmethod
    def find_by_id(cls, id):
        sql = "SELECT * FROM reviews WHERE id = ?"
        CURSOR.execute(sql, (id,))
        row = CURSOR.fetchone()
        if row:
            return cls.instance_from_db(row)
        return None

    def update(self):
        if self.id is not None:  # Ensures the review exists in the database
            sql = """
            UPDATE reviews
            SET year = ?, summary = ?, employee_id = ?
            WHERE id = ?
            """
            CURSOR.execute(sql, (self.year, self.summary, self.employee_id, self.id))
            CONN.commit()

    def delete(self):
        if self.id is not None:
            sql = "DELETE FROM reviews WHERE id = ?"
            CURSOR.execute(sql, (self.id,))
            CONN.commit()
            del Review.all[self.id]
            self.id = None

    @classmethod
    def get_all(cls):
        sql = "SELECT * FROM reviews"
        CURSOR.execute(sql)
        rows = CURSOR.fetchall()
        return [cls.instance_from_db(row) for row in rows]