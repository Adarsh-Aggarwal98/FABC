/**
 * SMSFDataSheet — SMSF Basic Data Sheet
 * All repeating sections (Members, Trustees, Nominations, Subsequent Events)
 * are fully dynamic: add / remove rows at will.
 */
import React, { useState, useEffect, useCallback } from 'react';
import { toast } from 'react-hot-toast';
import { smsfDataSheetAPI, clientEntitiesAPI } from '../../services/api';

// ─── constants ───────────────────────────────────────────────────────────────
const CURRENT_FY = new Date().getMonth() >= 6
  ? new Date().getFullYear() + 1
  : new Date().getFullYear();

const FY_OPTIONS = [CURRENT_FY, CURRENT_FY - 1, CURRENT_FY - 2, CURRENT_FY - 3].map(String);

const mkMember  = () => ({ name: '', address: '', dob: '', tfn: '', date_of_joining: '' });
const mkTrustee = () => ({ name: '', address: '', acn: '' });
const mkNom     = () => ({ nominee: '', relation: '', percentage: '' });
const mkEvent   = () => ({ date: '', name_of_event: '' });

// ─── tiny shared components ──────────────────────────────────────────────────
const Section = ({ title, action, children }) => (
  <div className="mb-5">
    <div className="flex items-center justify-between bg-primary-800 px-4 py-2 rounded-t-lg">
      <h2 className="text-sm font-bold uppercase tracking-wider text-white">{title}</h2>
      {action}
    </div>
    <div className="border border-gray-200 rounded-b-lg p-4 bg-white">{children}</div>
  </div>
);

const Lbl = ({ children }) => (
  <label className="block text-xs font-medium text-gray-600 mb-0.5">{children}</label>
);

const Inp = ({ value, onChange, placeholder }) => (
  <input
    value={value || ''}
    onChange={e => onChange(e.target.value)}
    placeholder={placeholder}
    className="w-full border border-gray-300 rounded-md px-2.5 py-1.5 text-sm
               focus:outline-none focus:border-primary-500 focus:ring-1 focus:ring-primary-200"
  />
);

const Textarea = ({ value, onChange, placeholder, rows = 2 }) => (
  <textarea
    value={value || ''}
    onChange={e => onChange(e.target.value)}
    placeholder={placeholder}
    rows={rows}
    className="w-full border border-gray-300 rounded-md px-2.5 py-1.5 text-sm
               focus:outline-none focus:border-primary-500 focus:ring-1 focus:ring-primary-200 resize-none"
  />
);

const AddBtn = ({ onClick, label }) => (
  <button type="button" onClick={onClick}
    className="text-xs font-medium text-primary-600 hover:text-primary-800 hover:underline">
    + {label}
  </button>
);

const RemoveBtn = ({ onClick }) => (
  <button type="button" onClick={onClick}
    className="p-1 text-red-400 hover:text-red-600 hover:bg-red-50 rounded transition"
    title="Remove">
    ✕
  </button>
);

// ─── Member card ─────────────────────────────────────────────────────────────
function MemberCard({ index, data, onChange, onRemove, canRemove }) {
  const set = f => v => onChange({ ...data, [f]: v });
  return (
    <div className="border border-gray-200 rounded-lg bg-gray-50 overflow-hidden">
      <div className="flex items-center justify-between px-3 py-2 bg-primary-50 border-b border-gray-200">
        <span className="text-xs font-bold text-primary-700 uppercase">Member {index + 1}</span>
        {canRemove && <RemoveBtn onClick={onRemove} />}
      </div>
      <div className="p-3 grid grid-cols-2 gap-2">
        <div>
          <Lbl>Full Name *</Lbl>
          <Inp value={data.name} onChange={set('name')} placeholder="Full legal name" />
        </div>
        <div>
          <Lbl>Date of Birth</Lbl>
          <Inp value={data.dob} onChange={set('dob')} placeholder="DD/MM/YYYY" />
        </div>
        <div className="col-span-2">
          <Lbl>Address</Lbl>
          <Textarea value={data.address} onChange={set('address')}
            placeholder="Street, Suburb STATE Postcode" />
        </div>
        <div>
          <Lbl>TFN</Lbl>
          <Inp value={data.tfn} onChange={set('tfn')} placeholder="xxx xxx xxx" />
        </div>
        <div>
          <Lbl>Date of Joining</Lbl>
          <Inp value={data.date_of_joining} onChange={set('date_of_joining')} placeholder="DD/MM/YYYY" />
        </div>
      </div>
    </div>
  );
}

// ─── Trustee card ─────────────────────────────────────────────────────────────
function TrusteeCard({ index, data, onChange, onRemove, canRemove }) {
  const set = f => v => onChange({ ...data, [f]: v });
  return (
    <div className="border border-gray-200 rounded-lg bg-gray-50 overflow-hidden">
      <div className="flex items-center justify-between px-3 py-2 bg-primary-50 border-b border-gray-200">
        <span className="text-xs font-bold text-primary-700 uppercase">Trustee {index + 1}</span>
        {canRemove && <RemoveBtn onClick={onRemove} />}
      </div>
      <div className="p-3 space-y-2">
        <div>
          <Lbl>Name / Company Name *</Lbl>
          <Inp value={data.name} onChange={set('name')} placeholder="Individual or corporate trustee" />
        </div>
        <div>
          <Lbl>Address</Lbl>
          <Textarea value={data.address} onChange={set('address')}
            placeholder="Street, Suburb STATE Postcode" />
        </div>
        <div>
          <Lbl>ACN (if corporate trustee)</Lbl>
          <Inp value={data.acn} onChange={set('acn')} placeholder="xxx xxx xxx" />
        </div>
      </div>
    </div>
  );
}

// ─── Nomination rows for one member ──────────────────────────────────────────
function NominationBlock({ memberIndex, memberName, rows, onChange }) {
  const add    = () => onChange([...rows, mkNom()]);
  const remove = i  => onChange(rows.filter((_, idx) => idx !== i));
  const set    = (i, f, v) => {
    const a = [...rows]; a[i] = { ...a[i], [f]: v }; onChange(a);
  };

  return (
    <div className="mb-4 last:mb-0">
      <div className="flex items-center gap-2 mb-1.5">
        <span className="text-xs font-bold text-primary-700 uppercase">
          Member {memberIndex + 1}{memberName ? ` — ${memberName}` : ''}
        </span>
        <AddBtn onClick={add} label="Add nominee" />
      </div>

      {rows.length === 0 ? (
        <p className="text-xs text-gray-400 italic">No nominees added yet.</p>
      ) : (
        <table className="w-full text-sm border-collapse">
          <thead>
            <tr className="bg-gray-100">
              <th className="border border-gray-200 px-2 py-1.5 text-left text-xs font-medium text-gray-600">Nominee Name</th>
              <th className="border border-gray-200 px-2 py-1.5 text-left text-xs font-medium text-gray-600 w-32">Relation</th>
              <th className="border border-gray-200 px-2 py-1.5 text-left text-xs font-medium text-gray-600 w-20">%age</th>
              <th className="border border-gray-200 px-1 py-1.5 w-8"></th>
            </tr>
          </thead>
          <tbody>
            {rows.map((r, i) => (
              <tr key={i} className="hover:bg-gray-50">
                <td className="border border-gray-200 px-1 py-0.5">
                  <Inp value={r.nominee} onChange={v => set(i, 'nominee', v)} placeholder="Full name" />
                </td>
                <td className="border border-gray-200 px-1 py-0.5">
                  <Inp value={r.relation} onChange={v => set(i, 'relation', v)} placeholder="e.g. Spouse" />
                </td>
                <td className="border border-gray-200 px-1 py-0.5">
                  <Inp value={r.percentage} onChange={v => set(i, 'percentage', v)} placeholder="100%" />
                </td>
                <td className="border border-gray-200 px-1 py-0.5 text-center">
                  <RemoveBtn onClick={() => remove(i)} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

// ─── Main page ────────────────────────────────────────────────────────────────
export default function SMSFDataSheetPage() {
  const [entities,         setEntities]         = useState([]);
  const [sheets,           setSheets]           = useState([]);
  const [selectedEntityId, setSelectedEntityId] = useState('');
  const [selectedFY,       setSelectedFY]       = useState(String(CURRENT_FY));
  const [loading,          setLoading]          = useState(false);
  const [saving,           setSaving]           = useState(false);
  const [editingId,        setEditingId]        = useState(null);
  const [showForm,         setShowForm]         = useState(false);

  // ── form fields ────────────────────────────────────────────────────────────
  const [fundName,     setFundName]     = useState('');
  const [dateCreation, setDateCreation] = useState('');
  const [abn,          setAbn]          = useState('');
  const [tfn,          setTfn]          = useState('');
  const [members,      setMembers]      = useState([mkMember()]);
  const [trustees,     setTrustees]     = useState([mkTrustee()]);
  const [bareTrustee,  setBareTrustee]  = useState({ bare_trust_name: '', bare_trustee_name: '', address: '', acn: '' });
  const [nominations,  setNominations]  = useState([[]]);       // one array per member
  const [subEvents,    setSubEvents]    = useState([mkEvent()]);

  // ── load entities ──────────────────────────────────────────────────────────
  useEffect(() => {
    clientEntitiesAPI.list({ entity_type: 'SMSF', per_page: 500 })
      .then(r => setEntities(r.data?.entities || []))
      .catch(() => toast.error('Failed to load funds'));
  }, []);

  // ── load sheets for selected entity ───────────────────────────────────────
  const loadSheets = useCallback(() => {
    if (!selectedEntityId) return;
    setLoading(true);
    smsfDataSheetAPI.list({ client_entity_id: selectedEntityId })
      .then(r => setSheets(r.data?.data_sheets || []))
      .catch(() => toast.error('Failed to load data sheets'))
      .finally(() => setLoading(false));
  }, [selectedEntityId]);

  useEffect(() => { loadSheets(); }, [loadSheets]);

  // ── keep nominations array length in sync with members length ─────────────
  useEffect(() => {
    setNominations(prev => {
      const next = [...prev];
      while (next.length < members.length) next.push([]);
      return next.slice(0, members.length);
    });
  }, [members.length]);

  // ── entity select ──────────────────────────────────────────────────────────
  const handleEntityChange = id => {
    setSelectedEntityId(id);
    const e = entities.find(x => x.id === id);
    if (e) { setFundName(e.name || ''); setAbn(e.abn || ''); setTfn(e.tfn || ''); }
  };

  // ── member helpers ─────────────────────────────────────────────────────────
  const addMember    = () => setMembers(m => [...m, mkMember()]);
  const removeMember = i  => {
    setMembers(m => m.filter((_, idx) => idx !== i));
    setNominations(n => n.filter((_, idx) => idx !== i));
  };
  const updateMember = (i, val) => setMembers(m => { const a = [...m]; a[i] = val; return a; });

  // ── trustee helpers ────────────────────────────────────────────────────────
  const addTrustee    = () => setTrustees(t => [...t, mkTrustee()]);
  const removeTrustee = i  => setTrustees(t => t.filter((_, idx) => idx !== i));
  const updateTrustee = (i, val) => setTrustees(t => { const a = [...t]; a[i] = val; return a; });

  // ── nomination helpers ─────────────────────────────────────────────────────
  const updateNom = (i, val) => setNominations(n => { const a = [...n]; a[i] = val; return a; });

  // ── sub-event helpers ──────────────────────────────────────────────────────
  const addEvent    = () => setSubEvents(e => [...e, mkEvent()]);
  const removeEvent = i  => setSubEvents(e => e.filter((_, idx) => idx !== i));
  const updateEvent = (i, f, v) => setSubEvents(e => {
    const a = [...e]; a[i] = { ...a[i], [f]: v }; return a;
  });

  // ── bare trustee helpers ───────────────────────────────────────────────────
  const setBare = f => v => setBareTrustee(b => ({ ...b, [f]: v }));

  // ── reset ──────────────────────────────────────────────────────────────────
  const resetForm = () => {
    setFundName(''); setDateCreation(''); setAbn(''); setTfn('');
    setMembers([mkMember()]);
    setTrustees([mkTrustee()]);
    setBareTrustee({ bare_trust_name: '', bare_trustee_name: '', address: '', acn: '' });
    setNominations([[]]);
    setSubEvents([mkEvent()]);
  };

  // ── open new form ──────────────────────────────────────────────────────────
  const openNew = () => {
    if (!selectedEntityId) return toast.error('Select a fund first');
    setEditingId(null);
    resetForm();
    const e = entities.find(x => x.id === selectedEntityId);
    if (e) { setFundName(e.name || ''); setAbn(e.abn || ''); setTfn(e.tfn || ''); }
    setShowForm(true);
  };

  // ── open edit form ─────────────────────────────────────────────────────────
  const openEdit = sheet => {
    setEditingId(sheet.id);
    setSelectedFY(sheet.financial_year);
    setFundName(sheet.fund_name || '');
    setDateCreation(sheet.date_of_creation || '');
    setAbn(sheet.abn_of_smsf || '');
    setTfn(sheet.tfn_of_smsf || '');

    const ms = (sheet.members || []).length ? sheet.members : [mkMember()];
    setMembers(ms);

    const ts = (sheet.trustees || []).length ? sheet.trustees : [mkTrustee()];
    setTrustees(ts);

    setBareTrustee(sheet.bare_trustee || { bare_trust_name: '', bare_trustee_name: '', address: '', acn: '' });

    // nominations: one sub-array per member
    const savedNoms = sheet.nominations || [];
    const noms = ms.map((_, i) => savedNoms[i] || []);
    setNominations(noms);

    setSubEvents((sheet.subsequent_events || []).length ? sheet.subsequent_events : [mkEvent()]);
    setShowForm(true);
  };

  // ── payload ────────────────────────────────────────────────────────────────
  const buildPayload = () => ({
    client_entity_id:  selectedEntityId,
    financial_year:    selectedFY,
    fund_name:         fundName,
    date_of_creation:  dateCreation,
    abn_of_smsf:       abn,
    tfn_of_smsf:       tfn,
    members:           members.filter(m => m.name.trim()),
    trustees:          trustees.filter(t => t.name.trim()),
    bare_trustee:      bareTrustee,
    nominations,
    subsequent_events: subEvents.filter(e => e.date || e.name_of_event),
  });

  // ── save ───────────────────────────────────────────────────────────────────
  const handleSave = async () => {
    if (!selectedEntityId) return toast.error('No fund selected');
    if (!fundName.trim())  return toast.error('Fund name is required');
    setSaving(true);
    try {
      if (editingId) {
        await smsfDataSheetAPI.update(editingId, buildPayload());
        toast.success('Data sheet updated');
      } else {
        await smsfDataSheetAPI.create(buildPayload());
        toast.success('Data sheet saved');
      }
      setShowForm(false);
      loadSheets();
    } catch (err) {
      const msg = err.response?.data?.error || 'Failed to save';
      toast.error(err.response?.status === 409 ? msg + ' Use Edit instead.' : msg);
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async id => {
    if (!window.confirm('Delete this data sheet?')) return;
    try { await smsfDataSheetAPI.delete(id); toast.success('Deleted'); loadSheets(); }
    catch { toast.error('Delete failed'); }
  };

  const downloadPdf = async sheet => {
    try {
      const res  = await smsfDataSheetAPI.getPdf(sheet.id);
      const url  = URL.createObjectURL(new Blob([res.data], { type: 'application/pdf' }));
      const a    = document.createElement('a');
      a.href = url;
      a.download = `SMSF_DataSheet_${sheet.client_entity_name}_FY${sheet.financial_year}.pdf`;
      a.click();
      URL.revokeObjectURL(url);
    } catch { toast.error('PDF generation failed'); }
  };

  // ─── render ────────────────────────────────────────────────────────────────
  return (
    <div className="p-6 max-w-7xl mx-auto">

      {/* Page header */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">SMSF Basic Data Sheet</h1>
        <p className="text-sm text-gray-500 mt-0.5">
          Fund · Members · Trustees · Bare Trustee · Nominations · Subsequent Events
        </p>
      </div>

      {/* Fund + FY filter bar */}
      <div className="bg-white border border-gray-200 rounded-xl p-4 mb-5 flex flex-wrap gap-4 items-end">
        <div className="flex-1 min-w-56">
          <label className="text-xs font-medium text-gray-600 block mb-1">SMSF Fund</label>
          <select value={selectedEntityId} onChange={e => handleEntityChange(e.target.value)}
            className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm">
            <option value="">— Select fund —</option>
            {entities.map(e => <option key={e.id} value={e.id}>{e.name}</option>)}
          </select>
        </div>
        <div>
          <label className="text-xs font-medium text-gray-600 block mb-1">Financial Year</label>
          <select value={selectedFY} onChange={e => setSelectedFY(e.target.value)}
            className="border border-gray-300 rounded-lg px-3 py-2 text-sm">
            {FY_OPTIONS.map(fy => (
              <option key={fy} value={fy}>
                FY{fy} (01/07/{Number(fy) - 1} – 30/06/{fy})
              </option>
            ))}
          </select>
        </div>
        <button onClick={openNew}
          className="px-4 py-2 bg-primary-600 text-white rounded-lg text-sm font-medium hover:bg-primary-700 transition">
          + New Data Sheet
        </button>
      </div>

      {/* Saved sheets table */}
      {selectedEntityId && (
        <div className="bg-white border border-gray-200 rounded-xl overflow-hidden mb-6">
          {loading ? (
            <div className="p-8 text-center text-gray-400">Loading...</div>
          ) : sheets.length === 0 ? (
            <div className="p-8 text-center text-gray-400">No data sheets yet for this fund.</div>
          ) : (
            <table className="w-full text-sm">
              <thead className="bg-gray-50 border-b">
                <tr>
                  {['Fund', 'FY', 'ABN', 'Members', 'Trustees', 'Updated', ''].map(h => (
                    <th key={h} className="px-4 py-3 text-left font-medium text-gray-600">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {sheets.map(s => (
                  <tr key={s.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3 font-medium text-gray-900">{s.client_entity_name}</td>
                    <td className="px-4 py-3 text-gray-700">FY{s.financial_year}</td>
                    <td className="px-4 py-3 text-gray-500">{s.abn_of_smsf}</td>
                    <td className="px-4 py-3 text-gray-500">{(s.members || []).filter(m => m.name).length}</td>
                    <td className="px-4 py-3 text-gray-500">{(s.trustees || []).filter(t => t.name).length}</td>
                    <td className="px-4 py-3 text-gray-400 text-xs">
                      {s.updated_at ? new Date(s.updated_at).toLocaleDateString('en-AU') : '—'}
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex gap-1.5 justify-end">
                        <button onClick={() => openEdit(s)}
                          className="px-2 py-1 text-xs text-blue-600 border border-blue-200 rounded hover:bg-blue-50">Edit</button>
                        <button onClick={() => downloadPdf(s)}
                          className="px-2 py-1 text-xs text-green-600 border border-green-200 rounded hover:bg-green-50">PDF</button>
                        <button onClick={() => handleDelete(s.id)}
                          className="px-2 py-1 text-xs text-red-500 border border-red-200 rounded hover:bg-red-50">Delete</button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}

      {/* ══════════ FORM MODAL ══════════════════════════════════════════════ */}
      {showForm && (
        <div className="fixed inset-0 z-50 bg-black/50 overflow-y-auto">
          <div className="min-h-screen flex items-start justify-center p-4 py-8">
            <div className="bg-gray-50 rounded-2xl shadow-2xl w-full max-w-4xl">

              {/* sticky header */}
              <div className="sticky top-0 z-10 bg-white rounded-t-2xl border-b px-6 py-4
                              flex items-center justify-between">
                <div>
                  <h2 className="text-lg font-bold text-gray-900">SMSF Basic Data Sheet</h2>
                  <p className="text-xs text-gray-500">
                    {entities.find(e => e.id === selectedEntityId)?.name} — FY{selectedFY}
                  </p>
                </div>
                <div className="flex gap-2">
                  <button onClick={() => setShowForm(false)}
                    className="px-4 py-2 text-sm text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50">
                    Cancel
                  </button>
                  <button onClick={handleSave} disabled={saving}
                    className="px-4 py-2 text-sm bg-primary-600 text-white rounded-lg
                               hover:bg-primary-700 disabled:opacity-50 font-medium">
                    {saving ? 'Saving…' : editingId ? 'Update' : 'Save'}
                  </button>
                </div>
              </div>

              <div className="p-6 space-y-1">

                {/* ── 1. Fund Details ── */}
                <Section title="Fund Details">
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <Lbl>Name of SMSF *</Lbl>
                      <Inp value={fundName} onChange={setFundName} placeholder="e.g. Smith Family Super Fund" />
                    </div>
                    <div>
                      <Lbl>Date of Creation</Lbl>
                      <Inp value={dateCreation} onChange={setDateCreation} placeholder="DD/MM/YYYY" />
                    </div>
                    <div>
                      <Lbl>ABN of SMSF</Lbl>
                      <Inp value={abn} onChange={setAbn} placeholder="xx xxx xxx xxx" />
                    </div>
                    <div>
                      <Lbl>TFN of SMSF</Lbl>
                      <Inp value={tfn} onChange={setTfn} placeholder="xxx xxx xxx" />
                    </div>
                  </div>
                </Section>

                {/* ── 2. Members (dynamic) ── */}
                <Section
                  title={`Members' Detail (${members.length})`}
                  action={
                    <button type="button" onClick={addMember}
                      className="text-xs font-medium text-white/80 hover:text-white border border-white/30
                                 hover:border-white rounded px-2 py-1 transition">
                      + Add Member
                    </button>
                  }
                >
                  <div className="grid grid-cols-2 gap-3">
                    {members.map((m, i) => (
                      <MemberCard key={i} index={i} data={m}
                        onChange={val => updateMember(i, val)}
                        onRemove={() => removeMember(i)}
                        canRemove={members.length > 1} />
                    ))}
                  </div>
                  {members.length === 0 && (
                    <p className="text-xs text-gray-400 text-center py-4">No members yet.</p>
                  )}
                </Section>

                {/* ── 3. Trustees (dynamic) ── */}
                <Section
                  title={`Trustee Details (${trustees.length})`}
                  action={
                    <button type="button" onClick={addTrustee}
                      className="text-xs font-medium text-white/80 hover:text-white border border-white/30
                                 hover:border-white rounded px-2 py-1 transition">
                      + Add Trustee
                    </button>
                  }
                >
                  <div className="grid grid-cols-2 gap-3">
                    {trustees.map((t, i) => (
                      <TrusteeCard key={i} index={i} data={t}
                        onChange={val => updateTrustee(i, val)}
                        onRemove={() => removeTrustee(i)}
                        canRemove={trustees.length > 1} />
                    ))}
                  </div>
                  {trustees.length === 0 && (
                    <p className="text-xs text-gray-400 text-center py-4">No trustees yet.</p>
                  )}
                </Section>

                {/* ── 4. Bare Trustee ── */}
                <Section title="Bare Trustee Details">
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <Lbl>Bare Trust Name</Lbl>
                      <Inp value={bareTrustee.bare_trust_name} onChange={setBare('bare_trust_name')}
                        placeholder="Name of bare trust" />
                    </div>
                    <div>
                      <Lbl>Bare Trustee (name / company)</Lbl>
                      <Inp value={bareTrustee.bare_trustee_name} onChange={setBare('bare_trustee_name')}
                        placeholder="e.g. XYZ Investments Pty Ltd" />
                    </div>
                    <div>
                      <Lbl>Address</Lbl>
                      <Textarea value={bareTrustee.address} onChange={setBare('address')}
                        placeholder="Street, Suburb STATE Postcode" />
                    </div>
                    <div>
                      <Lbl>A.C.N. (if company)</Lbl>
                      <Inp value={bareTrustee.acn} onChange={setBare('acn')} placeholder="xxx xxx xxx" />
                    </div>
                  </div>
                </Section>

                {/* ── 5. Nominations (synced with members) ── */}
                <Section title="Nomination Details">
                  <p className="text-xs text-gray-500 mb-3">
                    Binding death benefit nominations per member. Sections update automatically when members are added or removed.
                  </p>
                  {members.length === 0 ? (
                    <p className="text-xs text-gray-400 italic">Add members first to enter nominations.</p>
                  ) : (
                    members.map((m, i) => (
                      <NominationBlock
                        key={i}
                        memberIndex={i}
                        memberName={m.name}
                        rows={nominations[i] || []}
                        onChange={val => updateNom(i, val)}
                      />
                    ))
                  )}
                </Section>

                {/* ── 6. Subsequent Events (dynamic) ── */}
                <Section
                  title={`Subsequent Events (${subEvents.filter(e => e.date || e.name_of_event).length})`}
                  action={
                    <button type="button" onClick={addEvent}
                      className="text-xs font-medium text-white/80 hover:text-white border border-white/30
                                 hover:border-white rounded px-2 py-1 transition">
                      + Add Event
                    </button>
                  }
                >
                  {subEvents.length === 0 ? (
                    <p className="text-xs text-gray-400 italic">No events recorded.</p>
                  ) : (
                    <table className="w-full text-sm border-collapse">
                      <thead>
                        <tr className="bg-gray-100">
                          <th className="border border-gray-200 px-2 py-1.5 text-left text-xs font-medium text-gray-600 w-36">Date</th>
                          <th className="border border-gray-200 px-2 py-1.5 text-left text-xs font-medium text-gray-600">Name of Event</th>
                          <th className="border border-gray-200 px-1 py-1.5 w-8"></th>
                        </tr>
                      </thead>
                      <tbody>
                        {subEvents.map((ev, i) => (
                          <tr key={i} className="hover:bg-gray-50">
                            <td className="border border-gray-200 px-1 py-0.5">
                              <Inp value={ev.date} onChange={v => updateEvent(i, 'date', v)} placeholder="DD/MM/YYYY" />
                            </td>
                            <td className="border border-gray-200 px-1 py-0.5">
                              <Inp value={ev.name_of_event} onChange={v => updateEvent(i, 'name_of_event', v)}
                                placeholder="Description of event" />
                            </td>
                            <td className="border border-gray-200 px-1 py-0.5 text-center">
                              <RemoveBtn onClick={() => removeEvent(i)} />
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  )}
                </Section>

              </div>{/* /p-6 */}

              {/* sticky footer */}
              <div className="sticky bottom-0 bg-white rounded-b-2xl border-t px-6 py-3 flex justify-end gap-3">
                <button onClick={() => setShowForm(false)}
                  className="px-4 py-2 text-sm text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50">
                  Cancel
                </button>
                <button onClick={handleSave} disabled={saving}
                  className="px-5 py-2 text-sm bg-primary-600 text-white rounded-lg
                             hover:bg-primary-700 disabled:opacity-50 font-medium">
                  {saving ? 'Saving…' : editingId ? 'Update Data Sheet' : 'Save Data Sheet'}
                </button>
              </div>

            </div>
          </div>
        </div>
      )}

    </div>
  );
}
