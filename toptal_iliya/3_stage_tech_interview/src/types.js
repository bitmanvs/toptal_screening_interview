/**
 * @typedef {{
 *   product_id: number;
 *   product_name: string;
 *   product_category: string;
 *   quantity: number;
 *   unit_price: number;
 * }} OrderItem
 *
 * @typedef {{
 *   line: string;
 *   city: string;
 *   state: string;
 *   postal_code: string;
 *   country: string;
 * }} ShippingAddress
 *
 * @typedef {{
 *   order_id: number;
 *   order_number: number;
 *   customer_id: number;
 *   customer_name: string;
 *   seller_id: number;
 *   seller_name: string;
 *   order_items: OrderItem[];
 *   shipping_address: ShippingAddress;
 *   loyalty_points: number;
 *   order_status?: string;
 *   created_at: string;
 *   updated_at: string;
 * }} Order
 */

export {};
