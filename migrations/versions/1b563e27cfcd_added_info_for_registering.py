"""added info for registering

Revision ID: 1b563e27cfcd
Revises: 
Create Date: 2017-12-17 19:32:38.929773

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1b563e27cfcd'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('users')
    op.drop_constraint('personalCollections_user_id_fkey', 'personalCollections', type_='foreignkey')
    op.create_foreign_key(None, 'personalCollections', 'user', ['user_id'], ['id'])
    op.add_column('user', sa.Column('password_hash', sa.String(length=128), nullable=True))
    op.create_index(op.f('ix_user_dod_username'), 'user', ['dod_username'], unique=True)
    op.create_index(op.f('ix_user_email_address'), 'user', ['email_address'], unique=True)
    op.drop_constraint('user_dod_username_key', 'user', type_='unique')
    op.drop_constraint('user_email_address_key', 'user', type_='unique')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint('user_email_address_key', 'user', ['email_address'])
    op.create_unique_constraint('user_dod_username_key', 'user', ['dod_username'])
    op.drop_index(op.f('ix_user_email_address'), table_name='user')
    op.drop_index(op.f('ix_user_dod_username'), table_name='user')
    op.drop_column('user', 'password_hash')
    op.drop_constraint(None, 'personalCollections', type_='foreignkey')
    op.create_foreign_key('personalCollections_user_id_fkey', 'personalCollections', 'users', ['user_id'], ['id'])
    op.create_table('users',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('username', sa.VARCHAR(length=255), autoincrement=False, nullable=True),
    sa.Column('email', sa.VARCHAR(length=64), autoincrement=False, nullable=True),
    sa.Column('password_hash', sa.VARCHAR(length=128), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='users_pkey')
    )
    # ### end Alembic commands ###
