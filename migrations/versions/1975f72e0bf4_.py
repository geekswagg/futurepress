"""empty message

Revision ID: 1975f72e0bf4
Revises: 23f24d4c34b
Create Date: 2014-05-06 21:09:15.759478

"""

# revision identifiers, used by Alembic.
revision = '1975f72e0bf4'
down_revision = '23f24d4c34b'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('app_users', 'test_column')
    op.add_column('books', sa.Column('description', sa.String(length=1024), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('books', 'description')
    op.add_column('app_users', sa.Column('test_column', mysql.VARCHAR(length=1024), nullable=True))
    ### end Alembic commands ###
