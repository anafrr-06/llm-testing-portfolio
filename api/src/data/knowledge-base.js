/**
 * Simulated knowledge base for an e-commerce company
 * Used for RAG (Retrieval Augmented Generation) testing
 */

const documents = [
  {
    id: 'policy-returns',
    title: 'Return Policy',
    content: 'Products can be returned within 30 days of purchase with original receipt. Items must be unused and in original packaging. Refunds are processed within 5-7 business days.',
    category: 'policies'
  },
  {
    id: 'policy-shipping',
    title: 'Shipping Information',
    content: 'Standard shipping takes 5-7 business days. Express shipping (2-3 days) costs $9.99. Free shipping on orders over $50. International shipping available to select countries.',
    category: 'policies'
  },
  {
    id: 'policy-warranty',
    title: 'Warranty Policy',
    content: 'All electronics come with a 1-year manufacturer warranty. Extended warranty available for purchase. Warranty does not cover accidental damage.',
    category: 'policies'
  },
  {
    id: 'product-laptop-pro',
    title: 'Laptop Pro X1',
    content: 'Laptop Pro X1: 15.6" display, Intel i7 processor, 16GB RAM, 512GB SSD. Price: $1,299. Available in silver and space gray. Battery life up to 10 hours.',
    category: 'products'
  },
  {
    id: 'product-headphones',
    title: 'Wireless Headphones Max',
    content: 'Wireless Headphones Max: Active noise cancellation, 30-hour battery life, Bluetooth 5.0. Price: $249. Colors: black, white, blue.',
    category: 'products'
  },
  {
    id: 'support-contact',
    title: 'Contact Support',
    content: 'Customer support available 24/7. Phone: 1-800-555-0123. Email: support@techstore.com. Live chat available on website.',
    category: 'support'
  },
  {
    id: 'promo-current',
    title: 'Current Promotions',
    content: 'Summer Sale: 20% off all accessories until August 31st. Use code SUMMER20 at checkout. Cannot be combined with other offers.',
    category: 'promotions'
  }
];

function getAllDocuments() {
  return documents;
}

function search(query) {
  const queryLower = query.toLowerCase();
  return documents.filter(doc =>
    doc.title.toLowerCase().includes(queryLower) ||
    doc.content.toLowerCase().includes(queryLower) ||
    doc.category.toLowerCase().includes(queryLower)
  );
}

function getById(id) {
  return documents.find(doc => doc.id === id);
}

module.exports = {
  getAllDocuments,
  search,
  getById,
  documents
};
