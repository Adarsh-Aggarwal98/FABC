import React, { useState, useEffect } from 'react';
import {
  PlusIcon,
  PencilSquareIcon,
  TrashIcon,
  EyeIcon,
  StarIcon,
  XMarkIcon,
  CheckIcon,
} from '@heroicons/react/24/outline';
import { blogAPI } from '../../services/api';
import DashboardLayout from '../../components/layout/DashboardLayout';
import toast from 'react-hot-toast';

const CATEGORIES = ['Compliance', 'Practice Growth', 'Tax Tips', 'SMSF', 'ATO Updates', 'News'];

const emptyForm = {
  title: '', slug: '', excerpt: '', content: '', category: '',
  author: '', readTime: '5 min read', image: '', featured: false, published: true,
};

function slugify(str) {
  return str.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '');
}

export default function BlogManagement() {
  const [blogs, setBlogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editing, setEditing] = useState(null); // null = create, object = edit
  const [form, setForm] = useState(emptyForm);
  const [saving, setSaving] = useState(false);
  const [deleting, setDeleting] = useState(null);

  const fetchBlogs = async () => {
    try {
      setLoading(true);
      const res = await blogAPI.adminList();
      setBlogs(res.data?.blogs || []);
    } catch {
      toast.error('Failed to load blogs');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchBlogs(); }, []);

  const openCreate = () => {
    setEditing(null);
    setForm(emptyForm);
    setShowModal(true);
  };

  const openEdit = (blog) => {
    setEditing(blog);
    setForm({
      title: blog.title || '',
      slug: blog.slug || '',
      excerpt: blog.excerpt || '',
      content: blog.content || '',
      category: blog.category || '',
      author: blog.author || '',
      readTime: blog.readTime || '5 min read',
      image: blog.image || '',
      featured: blog.featured || false,
      published: blog.published !== false,
    });
    setShowModal(true);
  };

  const handleTitleChange = (val) => {
    setForm(f => ({
      ...f,
      title: val,
      slug: editing ? f.slug : slugify(val),
    }));
  };

  const handleSave = async (e) => {
    e.preventDefault();
    if (!form.title || !form.slug || !form.excerpt || !form.category || !form.author) {
      toast.error('Please fill in all required fields');
      return;
    }
    try {
      setSaving(true);
      if (editing) {
        await blogAPI.update(editing.id, form);
        toast.success('Blog updated');
      } else {
        await blogAPI.create(form);
        toast.success('Blog created');
      }
      setShowModal(false);
      fetchBlogs();
    } catch (err) {
      toast.error(err.response?.data?.error || 'Save failed');
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this blog post?')) return;
    try {
      setDeleting(id);
      await blogAPI.delete(id);
      toast.success('Blog deleted');
      fetchBlogs();
    } catch {
      toast.error('Delete failed');
    } finally {
      setDeleting(null);
    }
  };

  const togglePublished = async (blog) => {
    try {
      await blogAPI.update(blog.id, { published: !blog.published });
      fetchBlogs();
    } catch {
      toast.error('Failed to update');
    }
  };

  const inputCls = 'w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500';
  const labelCls = 'block text-xs font-medium text-gray-600 mb-1';

  return (
    <DashboardLayout>
      <div className="p-6">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Blog Management</h1>
            <p className="text-sm text-gray-500 mt-1">Manage articles shown on the AusSuperSource website</p>
          </div>
          <button
            onClick={openCreate}
            className="flex items-center gap-2 bg-primary-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-primary-700 transition-colors"
          >
            <PlusIcon className="h-4 w-4" />
            New Blog Post
          </button>
        </div>

        {/* Table */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
          {loading ? (
            <div className="flex items-center justify-center h-48">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600" />
            </div>
          ) : blogs.length === 0 ? (
            <div className="text-center py-16 text-gray-400">
              <PencilSquareIcon className="h-10 w-10 mx-auto mb-3 opacity-30" />
              <p>No blog posts yet. Create your first one!</p>
            </div>
          ) : (
            <table className="w-full text-sm">
              <thead className="bg-gray-50 border-b border-gray-200">
                <tr>
                  <th className="text-left px-4 py-3 font-semibold text-gray-600">Title</th>
                  <th className="text-left px-4 py-3 font-semibold text-gray-600">Category</th>
                  <th className="text-left px-4 py-3 font-semibold text-gray-600">Author</th>
                  <th className="text-center px-4 py-3 font-semibold text-gray-600">Status</th>
                  <th className="text-center px-4 py-3 font-semibold text-gray-600">Featured</th>
                  <th className="text-left px-4 py-3 font-semibold text-gray-600">Date</th>
                  <th className="text-right px-4 py-3 font-semibold text-gray-600">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {blogs.map(blog => (
                  <tr key={blog.id} className="hover:bg-gray-50 transition-colors">
                    <td className="px-4 py-3">
                      <div className="font-medium text-gray-900 truncate max-w-xs">{blog.title}</div>
                      <div className="text-xs text-gray-400">/{blog.slug}</div>
                    </td>
                    <td className="px-4 py-3">
                      <span className="px-2 py-0.5 bg-blue-100 text-blue-700 rounded-full text-xs">{blog.category}</span>
                    </td>
                    <td className="px-4 py-3 text-gray-600">{blog.author}</td>
                    <td className="px-4 py-3 text-center">
                      <button
                        onClick={() => togglePublished(blog)}
                        className={`px-2 py-0.5 rounded-full text-xs font-medium ${
                          blog.published ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'
                        }`}
                      >
                        {blog.published ? 'Published' : 'Draft'}
                      </button>
                    </td>
                    <td className="px-4 py-3 text-center">
                      {blog.featured && <StarIcon className="h-4 w-4 text-yellow-500 mx-auto" />}
                    </td>
                    <td className="px-4 py-3 text-gray-500 text-xs">
                      {blog.createdAt ? new Date(blog.createdAt).toLocaleDateString() : '—'}
                    </td>
                    <td className="px-4 py-3 text-right">
                      <div className="flex items-center justify-end gap-2">
                        <button
                          onClick={() => openEdit(blog)}
                          className="text-gray-400 hover:text-primary-600 transition-colors"
                          title="Edit"
                        >
                          <PencilSquareIcon className="h-4 w-4" />
                        </button>
                        <button
                          onClick={() => handleDelete(blog.id)}
                          disabled={deleting === blog.id}
                          className="text-gray-400 hover:text-red-500 transition-colors disabled:opacity-40"
                          title="Delete"
                        >
                          <TrashIcon className="h-4 w-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>

      {/* Create / Edit Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 bg-black/40 flex items-start justify-center p-4 overflow-y-auto">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-3xl my-6">
            <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between rounded-t-2xl z-10">
              <h2 className="text-lg font-bold text-gray-900">
                {editing ? 'Edit Blog Post' : 'New Blog Post'}
              </h2>
              <button onClick={() => setShowModal(false)}>
                <XMarkIcon className="h-6 w-6 text-gray-400 hover:text-gray-600" />
              </button>
            </div>

            <form onSubmit={handleSave} className="p-6 space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="col-span-2">
                  <label className={labelCls}>Title *</label>
                  <input className={inputCls} value={form.title}
                    onChange={e => handleTitleChange(e.target.value)} required />
                </div>
                <div>
                  <label className={labelCls}>Slug *</label>
                  <input className={inputCls} value={form.slug}
                    onChange={e => setForm(f => ({ ...f, slug: e.target.value }))} required />
                </div>
                <div>
                  <label className={labelCls}>Category *</label>
                  <select className={inputCls} value={form.category}
                    onChange={e => setForm(f => ({ ...f, category: e.target.value }))} required>
                    <option value="">Select category</option>
                    {CATEGORIES.map(c => <option key={c} value={c}>{c}</option>)}
                  </select>
                </div>
                <div>
                  <label className={labelCls}>Author *</label>
                  <input className={inputCls} value={form.author}
                    onChange={e => setForm(f => ({ ...f, author: e.target.value }))} required />
                </div>
                <div>
                  <label className={labelCls}>Read Time</label>
                  <input className={inputCls} value={form.readTime}
                    onChange={e => setForm(f => ({ ...f, readTime: e.target.value }))}
                    placeholder="5 min read" />
                </div>
                <div className="col-span-2">
                  <label className={labelCls}>Excerpt *</label>
                  <textarea className={inputCls} rows={2} value={form.excerpt}
                    onChange={e => setForm(f => ({ ...f, excerpt: e.target.value }))} required />
                </div>
                <div className="col-span-2">
                  <label className={labelCls}>Content (HTML or Markdown)</label>
                  <textarea className={`${inputCls} font-mono text-xs`} rows={8} value={form.content}
                    onChange={e => setForm(f => ({ ...f, content: e.target.value }))}
                    placeholder="Full article content..." />
                </div>
                <div className="col-span-2">
                  <label className={labelCls}>Image URL</label>
                  <input className={inputCls} value={form.image}
                    onChange={e => setForm(f => ({ ...f, image: e.target.value }))}
                    placeholder="https://..." />
                </div>
                <div className="flex items-center gap-4">
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input type="checkbox" className="rounded" checked={form.published}
                      onChange={e => setForm(f => ({ ...f, published: e.target.checked }))} />
                    <span className="text-sm text-gray-700">Published</span>
                  </label>
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input type="checkbox" className="rounded" checked={form.featured}
                      onChange={e => setForm(f => ({ ...f, featured: e.target.checked }))} />
                    <span className="text-sm text-gray-700">Featured</span>
                  </label>
                </div>
              </div>

              <div className="flex justify-end gap-3 pt-4 border-t border-gray-200">
                <button type="button" onClick={() => setShowModal(false)}
                  className="px-5 py-2 border border-gray-300 text-gray-700 rounded-lg text-sm hover:bg-gray-50">
                  Cancel
                </button>
                <button type="submit" disabled={saving}
                  className="px-6 py-2 bg-primary-600 text-white rounded-lg text-sm font-semibold hover:bg-primary-700 disabled:opacity-50">
                  {saving ? 'Saving...' : (editing ? 'Update Post' : 'Create Post')}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </DashboardLayout>
  );
}
