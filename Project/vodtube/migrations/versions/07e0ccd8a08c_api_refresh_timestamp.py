"""api refresh timestamp

Revision ID: 07e0ccd8a08c
Revises: e3231c65260c
Create Date: 2019-09-16 16:52:09.902268

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '07e0ccd8a08c'
down_revision = 'e3231c65260c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('last_api_update', sa.DateTime(), nullable=True))
    op.create_index(op.f('ix_user_last_api_update'), 'user', ['last_api_update'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_user_last_api_update'), table_name='user')
    op.drop_column('user', 'last_api_update')
    # ### end Alembic commands ###
