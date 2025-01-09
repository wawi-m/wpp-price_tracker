"""Add price fields to product model

Revision ID: bcfa8a1edd4e
Revises: 5dbd1d9a5024
Create Date: 2025-01-09 04:58:30.045987

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy import text
from datetime import datetime

# revision identifiers, used by Alembic.
revision = 'bcfa8a1edd4e'
down_revision = '5dbd1d9a5024'
branch_labels = None
depends_on = None


def upgrade():
    # Create temporary columns first
    with op.batch_alter_table('product', schema=None) as batch_op:
        batch_op.add_column(sa.Column('current_price', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('currency', sa.String(length=3), nullable=True))
        batch_op.add_column(sa.Column('last_price_update', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('price_history', sa.JSON(), nullable=True))

    # Get connection
    connection = op.get_bind()

    # Update existing products with their latest price
    connection.execute(text("""
        UPDATE product p
        SET current_price = (
            SELECT price
            FROM price
            WHERE product_id = p.id
            ORDER BY timestamp DESC
            LIMIT 1
        ),
        currency = 'KES',
        last_price_update = (
            SELECT timestamp
            FROM price
            WHERE product_id = p.id
            ORDER BY timestamp DESC
            LIMIT 1
        ),
        price_history = (
            SELECT json_agg(json_build_object(
                'price', price,
                'timestamp', timestamp
            ) ORDER BY timestamp)
            FROM price
            WHERE product_id = p.id
        )
    """))

    # Set default values for any products without prices
    connection.execute(text("""
        UPDATE product
        SET current_price = 0,
            currency = 'KES',
            last_price_update = NOW(),
            price_history = '[]'::json
        WHERE current_price IS NULL
    """))

    # Make current_price not nullable
    with op.batch_alter_table('product', schema=None) as batch_op:
        batch_op.alter_column('current_price',
               existing_type=sa.Float(),
               nullable=False)

    # Drop the price table
    op.drop_table('price')


def downgrade():
    # Create price table
    op.create_table('price',
        sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column('product_id', sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column('price', sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=False),
        sa.Column('currency', sa.VARCHAR(length=3), autoincrement=False, nullable=True),
        sa.Column('timestamp', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
        sa.ForeignKeyConstraint(['product_id'], ['product.id'], name='price_product_id_fkey'),
        sa.PrimaryKeyConstraint('id', name='price_pkey')
    )

    # Get connection
    connection = op.get_bind()

    # Insert price history back into price table
    connection.execute(text("""
        INSERT INTO price (product_id, price, currency, timestamp)
        SELECT p.id, 
               (ph->>'price')::float,
               p.currency,
               (ph->>'timestamp')::timestamp
        FROM product p,
             jsonb_array_elements(price_history::jsonb) ph
        WHERE price_history IS NOT NULL
    """))

    # Drop new columns from product table
    with op.batch_alter_table('product', schema=None) as batch_op:
        batch_op.drop_column('price_history')
        batch_op.drop_column('last_price_update')
        batch_op.drop_column('currency')
        batch_op.drop_column('current_price')
