"""Added is_header in PageForm

Revision ID: 14b085378a3c
Revises: 968b1aa54434
Create Date: 2024-01-06 14:19:10.040209

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '14b085378a3c'
down_revision = '968b1aa54434'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('page', schema=None) as batch_op:
        batch_op.add_column(sa.Column('is_header', sa.Boolean(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('page', schema=None) as batch_op:
        batch_op.drop_column('is_header')

    # ### end Alembic commands ###
