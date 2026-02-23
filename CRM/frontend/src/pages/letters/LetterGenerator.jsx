/**
 * LetterGenerator — Create, manage, sign, and download SMSF audit letters.
 * Letters are always tied to a specific ClientEntity (fund) and financial year,
 * ensuring each PDF is generated with that fund's actual data.
 */
import React, { useState, useEffect, useCallback } from 'react';
import { toast } from 'react-hot-toast';
import SignaturePad from '../../components/letters/SignaturePad';
import { lettersAPI, clientEntitiesAPI } from '../../services/api';

const CURRENT_FY = new Date().getMonth() >= 6 ? new Date().getFullYear() + 1 : new Date().getFullYear();
const FY_OPTIONS = [CURRENT_FY, CURRENT_FY - 1, CURRENT_FY - 2].map(String);

const STATUS_BADGE = {
  draft:   'bg-yellow-100 text-yellow-800',
  sent:    'bg-blue-100 text-blue-800',
  signed:  'bg-green-100 text-green-800',
};

// ─── Inline TrusteeRow editor ────────────────────────────────────────────────
function TrusteeRow({ trustee, index, onChange, onRemove }) {
  return (
    <div className="flex gap-2 items-start bg-gray-50 rounded p-2 mb-2">
      <div className="flex-1 grid grid-cols-3 gap-2">
        <input
          placeholder="Full name *"
          value={trustee.name || ''}
          onChange={e => onChange(index, 'name', e.target.value)}
          className="input-sm col-span-1"
        />
        <input
          placeholder="Company (if corporate trustee)"
          value={trustee.company || ''}
          onChange={e => onChange(index, 'company', e.target.value)}
          className="input-sm col-span-1"
        />
        <input
          placeholder="Role (e.g. Trustee, Director)"
          value={trustee.role || ''}
          onChange={e => onChange(index, 'role', e.target.value)}
          className="input-sm col-span-1"
        />
      </div>
      <button
        type="button"
        onClick={() => onRemove(index)}
        className="text-red-400 hover:text-red-600 text-sm mt-1"
        title="Remove trustee"
      >
        ×
      </button>
    </div>
  );
}

// ─── Main component ──────────────────────────────────────────────────────────
export default function LetterGenerator() {
  // ── State ──
  const [entities, setEntities] = useState([]);
  const [letters, setLetters] = useState([]);
  const [loadingEntities, setLoadingEntities] = useState(true);
  const [loadingLetters, setLoadingLetters] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  // Filter
  const [filterEntityId, setFilterEntityId] = useState('');
  const [filterType, setFilterType] = useState('');
  const [filterStatus, setFilterStatus] = useState('');

  // Create form
  const [showCreate, setShowCreate] = useState(false);
  const [form, setForm] = useState({
    client_entity_id: '',
    letter_type: 'engagement',
    financial_year: String(CURRENT_FY),
    letter_date: new Date().toLocaleDateString('en-AU', { day: '2-digit', month: 'long', year: 'numeric' }),
    auditor_name: 'AusSuperSource',
    auditor_registration: '',
    auditor_address: '',
    trustees: [{ name: '', company: '', role: 'Trustee' }],
  });

  // Sign modal
  const [signModal, setSignModal] = useState(null);  // { letter, trusteeIndex }
  const [uploadModal, setUploadModal] = useState(null);
  const [previewModal, setPreviewModal] = useState(null);

  // ── Load fund entities ──
  useEffect(() => {
    clientEntitiesAPI.list({ entity_type: 'SMSF', per_page: 500 })
      .then(res => {
        const data = res.data?.entities || res.data?.data || res.data || [];
        setEntities(Array.isArray(data) ? data : []);
      })
      .catch(() => toast.error('Failed to load client entities'))
      .finally(() => setLoadingEntities(false));
  }, []);

  // ── Load letters ──
  const loadLetters = useCallback(() => {
    setLoadingLetters(true);
    const params = {};
    if (filterEntityId) params.client_entity_id = filterEntityId;
    if (filterType) params.letter_type = filterType;
    if (filterStatus) params.status = filterStatus;

    lettersAPI.list(params)
      .then(res => setLetters(res.data?.letters || []))
      .catch(() => toast.error('Failed to load letters'))
      .finally(() => setLoadingLetters(false));
  }, [filterEntityId, filterType, filterStatus]);

  useEffect(() => { loadLetters(); }, [loadLetters]);

  // ── When entity is selected in form, prefill trustee name ──
  const handleEntityChange = (entityId) => {
    const entity = entities.find(e => e.id === entityId);
    const trustees = entity?.trustee_name
      ? [{ name: entity.trustee_name, company: '', role: 'Trustee' }]
      : [{ name: '', company: '', role: 'Trustee' }];
    setForm(f => ({ ...f, client_entity_id: entityId, trustees }));
  };

  // ── Trustee helpers ──
  const updateTrustee = (i, field, val) =>
    setForm(f => { const t = [...f.trustees]; t[i] = { ...t[i], [field]: val }; return { ...f, trustees: t }; });

  const removeTrustee = (i) =>
    setForm(f => ({ ...f, trustees: f.trustees.filter((_, idx) => idx !== i) }));

  const addTrustee = () =>
    setForm(f => ({ ...f, trustees: [...f.trustees, { name: '', company: '', role: 'Trustee' }] }));

  // ── Create letter ──
  const handleCreate = async (e) => {
    e.preventDefault();
    if (!form.client_entity_id) return toast.error('Please select a fund');
    if (!form.financial_year) return toast.error('Financial year is required');
    if (!form.trustees[0]?.name) return toast.error('At least one trustee name is required');

    setSubmitting(true);
    try {
      await lettersAPI.create(form);
      toast.success('Letter created successfully');
      setShowCreate(false);
      setForm(f => ({ ...f, client_entity_id: '', trustees: [{ name: '', company: '', role: 'Trustee' }] }));
      loadLetters();
    } catch (err) {
      toast.error(err.response?.data?.error || 'Failed to create letter');
    } finally {
      setSubmitting(false);
    }
  };

  // ── Download PDF ──
  const downloadPdf = async (letter) => {
    try {
      const res = await lettersAPI.getPdf(letter.id);
      const blob = new Blob([res.data], { type: 'application/pdf' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${letter.client_entity_name}_${letter.letter_type}_FY${letter.financial_year}.pdf`;
      a.click();
      URL.revokeObjectURL(url);
    } catch {
      toast.error('Failed to generate PDF');
    }
  };

  // ── Delete letter ──
  const deleteLetter = async (id) => {
    if (!window.confirm('Delete this letter?')) return;
    try {
      await lettersAPI.delete(id);
      toast.success('Letter deleted');
      loadLetters();
    } catch {
      toast.error('Failed to delete');
    }
  };

  // ── Sign on screen ──
  const handleSign = async (base64) => {
    if (!signModal) return;
    try {
      await lettersAPI.sign(signModal.letter.id, {
        trustee_index: signModal.trusteeIndex,
        signature_b64: base64,
        signed_date: new Date().toLocaleDateString('en-AU'),
      });
      toast.success('Signature saved');
      setSignModal(null);
      loadLetters();
    } catch {
      toast.error('Failed to save signature');
    }
  };

  // ── Upload signed PDF ──
  const handleUpload = async (file) => {
    if (!uploadModal) return;
    const formData = new FormData();
    formData.append('file', file);
    try {
      await lettersAPI.uploadSigned(uploadModal.id, formData);
      toast.success('Signed PDF uploaded');
      setUploadModal(null);
      loadLetters();
    } catch {
      toast.error('Upload failed');
    }
  };

  // ─── Render ──────────────────────────────────────────────────────────────
  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Audit Letters</h1>
          <p className="text-sm text-gray-500 mt-0.5">
            Generate Engagement &amp; Trustee Representation letters per fund and financial year
          </p>
        </div>
        <button
          onClick={() => setShowCreate(true)}
          className="btn-primary flex items-center gap-1.5 px-4 py-2 bg-primary-600 text-white rounded-lg text-sm font-medium hover:bg-primary-700 transition"
        >
          + New Letter
        </button>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-3 mb-5 bg-white p-3 rounded-lg border border-gray-200">
        <select
          value={filterEntityId}
          onChange={e => setFilterEntityId(e.target.value)}
          className="input-sm text-sm"
        >
          <option value="">All Funds</option>
          {entities.map(e => <option key={e.id} value={e.id}>{e.name}</option>)}
        </select>
        <select value={filterType} onChange={e => setFilterType(e.target.value)} className="input-sm text-sm">
          <option value="">All Types</option>
          <option value="engagement">Engagement</option>
          <option value="representation">Representation</option>
        </select>
        <select value={filterStatus} onChange={e => setFilterStatus(e.target.value)} className="input-sm text-sm">
          <option value="">All Statuses</option>
          <option value="draft">Draft</option>
          <option value="sent">Sent</option>
          <option value="signed">Signed</option>
        </select>
      </div>

      {/* Letters Table */}
      <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
        {loadingLetters ? (
          <div className="p-10 text-center text-gray-400">Loading...</div>
        ) : letters.length === 0 ? (
          <div className="p-10 text-center">
            <p className="text-gray-400 mb-3">No letters found.</p>
            <button onClick={() => setShowCreate(true)}
              className="text-primary-600 text-sm hover:underline">
              Create the first one
            </button>
          </div>
        ) : (
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="px-4 py-3 text-left font-medium text-gray-600">Fund</th>
                <th className="px-4 py-3 text-left font-medium text-gray-600">Type</th>
                <th className="px-4 py-3 text-left font-medium text-gray-600">FY</th>
                <th className="px-4 py-3 text-left font-medium text-gray-600">Date</th>
                <th className="px-4 py-3 text-left font-medium text-gray-600">Status</th>
                <th className="px-4 py-3 text-left font-medium text-gray-600">Trustees</th>
                <th className="px-4 py-3 text-right font-medium text-gray-600">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {letters.map(letter => (
                <tr key={letter.id} className="hover:bg-gray-50 transition">
                  <td className="px-4 py-3 font-medium text-gray-900">{letter.client_entity_name}</td>
                  <td className="px-4 py-3 capitalize text-gray-700">{letter.letter_type}</td>
                  <td className="px-4 py-3 text-gray-700">FY{letter.financial_year}</td>
                  <td className="px-4 py-3 text-gray-500">{letter.letter_date}</td>
                  <td className="px-4 py-3">
                    <span className={`px-2 py-0.5 rounded-full text-xs font-medium capitalize ${STATUS_BADGE[letter.status]}`}>
                      {letter.status}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-gray-500">
                    {(letter.trustees_data || []).map((t, i) => (
                      <span key={i} className={`inline-block text-xs mr-1 ${t.signature_b64 ? 'text-green-600' : 'text-gray-400'}`}>
                        {t.name || `Trustee ${i + 1}`}{t.signature_b64 ? ' ✓' : ''}
                      </span>
                    ))}
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex gap-1.5 justify-end flex-wrap">
                      {/* Preview HTML */}
                      <button
                        onClick={() => setPreviewModal(letter)}
                        className="px-2 py-1 text-xs text-indigo-600 border border-indigo-200 rounded hover:bg-indigo-50 transition"
                      >
                        Preview
                      </button>
                      {/* Download PDF */}
                      <button
                        onClick={() => downloadPdf(letter)}
                        className="px-2 py-1 text-xs text-blue-600 border border-blue-200 rounded hover:bg-blue-50 transition"
                      >
                        Download PDF
                      </button>
                      {/* Sign online */}
                      <button
                        onClick={() => setSignModal({ letter, trusteeIndex: 0 })}
                        className="px-2 py-1 text-xs text-green-600 border border-green-200 rounded hover:bg-green-50 transition"
                      >
                        Sign Online
                      </button>
                      {/* Upload signed */}
                      <button
                        onClick={() => setUploadModal(letter)}
                        className="px-2 py-1 text-xs text-orange-600 border border-orange-200 rounded hover:bg-orange-50 transition"
                      >
                        Upload Signed
                      </button>
                      {/* Delete */}
                      <button
                        onClick={() => deleteLetter(letter.id)}
                        className="px-2 py-1 text-xs text-red-500 border border-red-200 rounded hover:bg-red-50 transition"
                      >
                        Delete
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* ─── Create Letter Modal ───────────────────────────────────── */}
      {showCreate && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <div className="bg-white rounded-xl shadow-xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between p-5 border-b">
              <h2 className="text-lg font-semibold text-gray-900">Create Audit Letter</h2>
              <button onClick={() => setShowCreate(false)} className="text-gray-400 hover:text-gray-600 text-xl">×</button>
            </div>
            <form onSubmit={handleCreate} className="p-5 space-y-4">
              {/* Fund */}
              <div>
                <label className="label-sm block mb-1 text-sm font-medium text-gray-700">
                  Fund (Client Entity) *
                </label>
                {loadingEntities ? (
                  <p className="text-sm text-gray-400">Loading funds...</p>
                ) : (
                  <select
                    required
                    value={form.client_entity_id}
                    onChange={e => handleEntityChange(e.target.value)}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"
                  >
                    <option value="">— Select SMSF fund —</option>
                    {entities.map(e => (
                      <option key={e.id} value={e.id}>{e.name} {e.abn ? `(ABN ${e.abn})` : ''}</option>
                    ))}
                  </select>
                )}
                <p className="text-xs text-gray-400 mt-0.5">
                  The PDF will be populated with this fund's name, ABN, address, and trustee data.
                </p>
              </div>

              {/* Letter type + FY */}
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Letter Type *</label>
                  <select
                    value={form.letter_type}
                    onChange={e => setForm(f => ({ ...f, letter_type: e.target.value }))}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"
                  >
                    <option value="engagement">Engagement Letter</option>
                    <option value="representation">Representation Letter</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Financial Year *</label>
                  <select
                    value={form.financial_year}
                    onChange={e => setForm(f => ({ ...f, financial_year: e.target.value }))}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"
                  >
                    {FY_OPTIONS.map(fy => (
                      <option key={fy} value={fy}>FY{fy} (01/07/{Number(fy)-1} – 30/06/{fy})</option>
                    ))}
                  </select>
                </div>
              </div>

              {/* Letter date */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Letter Date</label>
                <input
                  type="text"
                  value={form.letter_date}
                  onChange={e => setForm(f => ({ ...f, letter_date: e.target.value }))}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"
                  placeholder="e.g. 01 July 2025"
                />
              </div>

              {/* Auditor */}
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Auditor Name</label>
                  <input
                    type="text"
                    value={form.auditor_name}
                    onChange={e => setForm(f => ({ ...f, auditor_name: e.target.value }))}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">ASIC Registration No.</label>
                  <input
                    type="text"
                    value={form.auditor_registration}
                    onChange={e => setForm(f => ({ ...f, auditor_registration: e.target.value }))}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"
                    placeholder="e.g. 123456"
                  />
                </div>
              </div>

              {/* Trustees */}
              <div>
                <div className="flex items-center justify-between mb-1">
                  <label className="block text-sm font-medium text-gray-700">Trustees *</label>
                  <button type="button" onClick={addTrustee}
                    className="text-xs text-primary-600 hover:underline">
                    + Add trustee
                  </button>
                </div>
                {form.trustees.map((t, i) => (
                  <TrusteeRow key={i} trustee={t} index={i}
                    onChange={updateTrustee} onRemove={removeTrustee} />
                ))}
              </div>

              <div className="flex justify-end gap-3 pt-2">
                <button type="button" onClick={() => setShowCreate(false)}
                  className="px-4 py-2 text-sm text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50">
                  Cancel
                </button>
                <button type="submit" disabled={submitting}
                  className="px-4 py-2 text-sm bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50">
                  {submitting ? 'Creating...' : 'Create Letter'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* ─── Sign Modal ────────────────────────────────────────────── */}
      {signModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <div className="bg-white rounded-xl shadow-xl w-full max-w-lg">
            <div className="flex items-center justify-between p-5 border-b">
              <h2 className="text-lg font-semibold">Sign Letter Online</h2>
              <button onClick={() => setSignModal(null)} className="text-gray-400 hover:text-gray-600 text-xl">×</button>
            </div>
            <div className="p-5 space-y-4">
              <p className="text-sm text-gray-600">
                <strong>{signModal.letter.client_entity_name}</strong> —{' '}
                {signModal.letter.letter_type} FY{signModal.letter.financial_year}
              </p>
              {/* Trustee selector if multiple */}
              {signModal.letter.trustees_data?.length > 1 && (
                <div>
                  <label className="text-sm font-medium text-gray-700 block mb-1">Signing as</label>
                  <select
                    value={signModal.trusteeIndex}
                    onChange={e => setSignModal(s => ({ ...s, trusteeIndex: Number(e.target.value) }))}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"
                  >
                    {signModal.letter.trustees_data.map((t, i) => (
                      <option key={i} value={i}>{t.name || `Trustee ${i + 1}`}</option>
                    ))}
                  </select>
                </div>
              )}
              <SignaturePad
                onSave={handleSign}
                onClear={() => {}}
                width={400}
                height={150}
                label="Draw your signature"
                existingSignature={signModal.letter.trustees_data?.[signModal.trusteeIndex]?.signature_b64}
              />
              <p className="text-xs text-gray-400">
                Draw your signature above then click "Save Signature". The PDF will be regenerated with your
                embedded signature.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* ─── Upload Signed PDF Modal ───────────────────────────────── */}
      {uploadModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <div className="bg-white rounded-xl shadow-xl w-full max-w-md">
            <div className="flex items-center justify-between p-5 border-b">
              <h2 className="text-lg font-semibold">Upload Signed PDF</h2>
              <button onClick={() => setUploadModal(null)} className="text-gray-400 hover:text-gray-600 text-xl">×</button>
            </div>
            <div className="p-5 space-y-4">
              <p className="text-sm text-gray-600">
                Upload the physically signed version of the letter for{' '}
                <strong>{uploadModal.client_entity_name}</strong>.
              </p>
              <ol className="text-sm text-gray-500 space-y-1 list-decimal list-inside">
                <li>Download the PDF using the "Download PDF" button</li>
                <li>Print, sign, and scan the document</li>
                <li>Upload the signed PDF below</li>
              </ol>
              <label className="block">
                <span className="text-sm font-medium text-gray-700 block mb-2">Select signed PDF</span>
                <input
                  type="file"
                  accept="application/pdf"
                  onChange={e => e.target.files[0] && handleUpload(e.target.files[0])}
                  className="w-full text-sm text-gray-600 file:mr-3 file:py-1.5 file:px-3 file:border file:rounded file:text-xs file:font-medium file:bg-primary-50 file:text-primary-600 file:border-primary-200"
                />
              </label>
            </div>
          </div>
        </div>
      )}

      {/* ─── Preview Modal (HTML iframe) ──────────────────────────── */}
      {previewModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4">
          <div className="bg-white rounded-xl shadow-xl w-full max-w-4xl h-[90vh] flex flex-col">
            <div className="flex items-center justify-between p-4 border-b">
              <h2 className="text-base font-semibold text-gray-900">
                Preview — {previewModal.client_entity_name} {previewModal.letter_type} FY{previewModal.financial_year}
              </h2>
              <button onClick={() => setPreviewModal(null)} className="text-gray-400 hover:text-gray-600 text-xl">×</button>
            </div>
            <iframe
              src={`${import.meta.env.VITE_API_URL?.replace('/api', '')}/api/letters/${previewModal.id}/preview-html`}
              className="flex-1 w-full border-0"
              title="Letter Preview"
            />
          </div>
        </div>
      )}

      {/* Styles not in Tailwind */}
      <style>{`
        .input-sm {
          border: 1px solid #d1d5db;
          border-radius: 6px;
          padding: 5px 10px;
          font-size: 13px;
          outline: none;
          width: 100%;
        }
        .input-sm:focus { border-color: #1B72BE; }
      `}</style>
    </div>
  );
}
