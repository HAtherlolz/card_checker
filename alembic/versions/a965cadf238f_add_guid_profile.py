"""add_guid_profile

Revision ID: a965cadf238f
Revises: 06a562f41f34
Create Date: 2023-05-19 12:15:59.395750

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a965cadf238f'
down_revision = '06a562f41f34'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('profiles', sa.Column('guid', sa.String(length=255), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('profiles', 'guid')
    # ### end Alembic commands ###
