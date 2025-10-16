'use client'

import { useState, useEffect } from 'react'
import DashboardLayout from '@/components/DashboardLayout'
import api from '@/lib/api'
import { useRouter } from 'next/navigation'

interface Product {
  product_id: string
  product_name: string
  rate: number | string
  quantity: number
}

interface BillItem {
  product_id: string
  product_name: string
  quantity: number
  rate: number
  amount: number
}

interface PaymentType {
  payment_type_id: string
  type_name: string
}

export default function NonGSTBillingPage() {
  const router = useRouter()
  const [products, setProducts] = useState<Product[]>([])
  const [paymentTypes, setPaymentTypes] = useState<PaymentType[]>([])
  const [loading, setLoading] = useState(false)

  const [formData, setFormData] = useState({
    customer_name: '',
    customer_phone: '',
    payment_type: '',
  })

  const [items, setItems] = useState<BillItem[]>([])
  const [currentItem, setCurrentItem] = useState({
    product_id: '',
    product_name: '',
    quantity: 1,
    rate: 0,
  })

  useEffect(() => {
    fetchProducts()
    fetchPaymentTypes()
  }, [])

  const fetchProducts = async () => {
    try {
      const response = await api.get('/stock')
      setProducts(response.data.stock || [])
    } catch (error) {
      console.error('Failed to fetch products:', error)
    }
  }

  const fetchPaymentTypes = async () => {
    try {
      const response = await api.get('/payment/list')
      setPaymentTypes(response.data.payment_types || [])
    } catch (error) {
      console.error('Failed to fetch payment types:', error)
    }
  }

  const handleProductSelect = (productId: string) => {
    const product = products.find((p) => p.product_id === productId)
    if (product) {
      setCurrentItem({
        product_id: product.product_id,
        product_name: product.product_name,
        quantity: 1,
        rate: Number(product.rate),
      })
    }
  }

  const addItem = () => {
    if (!currentItem.product_id || currentItem.quantity <= 0) {
      alert('Please select a product and enter valid quantity')
      return
    }

    const amount = currentItem.quantity * currentItem.rate
    setItems([...items, { ...currentItem, amount }])
    setCurrentItem({
      product_id: '',
      product_name: '',
      quantity: 1,
      rate: 0,
    })
  }

  const removeItem = (index: number) => {
    setItems(items.filter((_, i) => i !== index))
  }

  const calculateTotal = () => {
    return items.reduce((sum, item) => sum + item.amount, 0)
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (items.length === 0) {
      alert('Please add at least one item')
      return
    }

    if (!formData.payment_type) {
      alert('Please select a payment type')
      return
    }

    try {
      setLoading(true)
      await api.post('/billing/non-gst', {
        customer_name: formData.customer_name,
        customer_phone: formData.customer_phone,
        items: items,
        total_amount: calculateTotal(),
        payment_type: formData.payment_type,
      })

      alert('Non-GST Bill created successfully!')
      router.push('/billing')
    } catch (error: any) {
      alert(error.response?.data?.error || 'Failed to create bill')
    } finally {
      setLoading(false)
    }
  }

  return (
    <DashboardLayout>
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Create Non-GST Bill</h1>
        <p className="mt-2 text-gray-600">Generate a new non-GST bill without tax calculation</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Customer Information */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Customer Information</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Customer Name *
              </label>
              <input
                type="text"
                required
                value={formData.customer_name}
                onChange={(e) =>
                  setFormData({ ...formData, customer_name: e.target.value })
                }
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Customer Phone *
              </label>
              <input
                type="tel"
                required
                value={formData.customer_phone}
                onChange={(e) =>
                  setFormData({ ...formData, customer_phone: e.target.value })
                }
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              />
            </div>
          </div>
        </div>

        {/* Add Items */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Add Items</h2>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Select Product
              </label>
              <select
                value={currentItem.product_id}
                onChange={(e) => handleProductSelect(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              >
                <option value="">Choose product</option>
                {products.map((product) => (
                  <option key={product.product_id} value={product.product_id}>
                    {product.product_name} (Stock: {product.quantity})
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Quantity
              </label>
              <input
                type="number"
                min="1"
                value={currentItem.quantity}
                onChange={(e) =>
                  setCurrentItem({ ...currentItem, quantity: parseInt(e.target.value) || 0 })
                }
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Rate (₹)
              </label>
              <input
                type="number"
                readOnly
                value={currentItem.rate}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg bg-gray-50"
              />
            </div>
            <div className="flex items-end">
              <button
                type="button"
                onClick={addItem}
                className="w-full px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition"
              >
                Add Item
              </button>
            </div>
          </div>

          {/* Items Table */}
          {items.length > 0 && (
            <div className="mt-6 overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Product
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Quantity
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Rate
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Amount
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Action
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {items.map((item, index) => (
                    <tr key={index}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {item.product_name}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {item.quantity}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        ₹{item.rate.toFixed(2)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 font-semibold">
                        ₹{item.amount.toFixed(2)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        <button
                          type="button"
                          onClick={() => removeItem(index)}
                          className="text-red-600 hover:text-red-800"
                        >
                          Remove
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Billing Details */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Billing Details</h2>
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Payment Type *
            </label>
            <select
              required
              value={formData.payment_type}
              onChange={(e) =>
                setFormData({ ...formData, payment_type: e.target.value })
              }
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            >
              <option value="">Select payment type</option>
              {paymentTypes.map((pt) => (
                <option key={pt.payment_type_id} value={pt.payment_type_id}>
                  {pt.type_name}
                </option>
              ))}
            </select>
          </div>

          {/* Bill Summary */}
          <div className="border-t pt-4">
            <div className="flex justify-between text-2xl font-bold">
              <span className="text-gray-900">Total Amount:</span>
              <span className="text-purple-600">₹{calculateTotal().toFixed(2)}</span>
            </div>
          </div>
        </div>

        {/* Submit Button */}
        <div className="flex gap-4">
          <button
            type="submit"
            disabled={loading}
            className="flex-1 px-8 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition disabled:bg-gray-400 text-lg font-semibold"
          >
            {loading ? 'Creating Bill...' : 'Create Non-GST Bill'}
          </button>
          <button
            type="button"
            onClick={() => router.push('/billing')}
            className="px-8 py-3 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition"
          >
            Cancel
          </button>
        </div>
      </form>
    </DashboardLayout>
  )
}
