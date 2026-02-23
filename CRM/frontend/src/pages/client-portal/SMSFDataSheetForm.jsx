/**
 * SMSFDataSheetForm — inline form for clients to fill SMSF Basic Data Sheet
 * Calls POST /api/client-portal/start-audit with the form data.
 */
import React, { useState } from 'react';
import { XMarkIcon, PlusIcon, TrashIcon } from '@heroicons/react/24/outline';
import { clientPortalAPI } from '../../services/api';
import toast from 'react-hot-toast';

const CURRENT_FY = new Date().getMonth() >= 6
  ? String(new Date().getFullYear() + 1)
  : String(new Date().getFullYear());

const emptyMember = () => ({ name: '', address: '', dob: '', tfn: '', date_of_joining: '' });
const emptyTrustee = () => ({ name: '', address: '', acn: '' });
const emptyNomination = () => ({ nominee: '', relation: '', percentage: '' });
const emptyEvent = () => ({ date: '', name_of_event: '' });

export default function SMSFDataSheetForm({ entity, onClose, onSubmitted }) {
  const [submitting, setSubmitting] = useState(false);
  const [fy, setFy] = useState(CURRENT_FY);
  const [fundName, setFundName] = useState(entity?.name || '');
  const [dateOfCreation, setDateOfCreation] = useState('');
  const [abn, setAbn] = useState(entity?.abn || '');
  const [tfn, setTfn] = useState(entity?.tfn || '');
  const [members, setMembers] = useState([emptyMember()]);
  const [trustees, setTrustees] = useState([emptyTrustee()]);
  const [bareTrustee, setBareTrustee] = useState({
    bare_trust_name: '', bare_trustee_name: '', address: '', acn: ''
  });
  const [nominations, setNominations] = useState([[emptyNomination()]]);
  const [events, setEvents] = useState([emptyEvent()]);

  // Keep nominations in sync with members
  const addMember = () => {
    setMembers(m => [...m, emptyMember()]);
    setNominations(n => [...n, [emptyNomination()]]);
  };
  const removeMember = (i) => {
    if (members.length === 1) return;
    setMembers(m => m.filter((_, idx) => idx !== i));
    setNominations(n => n.filter((_, idx) => idx !== i));
  };
  const updateMember = (i, field, val) =>
    setMembers(m => m.map((mb, idx) => idx === i ? { ...mb, [field]: val } : mb));

  const addTrustee = () => setTrustees(t => [...t, emptyTrustee()]);
  const removeTrustee = (i) => { if (trustees.length > 1) setTrustees(t => t.filter((_, idx) => idx !== i)); };
  const updateTrustee = (i, field, val) =>
    setTrustees(t => t.map((tr, idx) => idx === i ? { ...tr, [field]: val } : tr));

  const addNomination = (mi) =>
    setNominations(n => n.map((row, idx) => idx === mi ? [...row, emptyNomination()] : row));
  const removeNomination = (mi, ni) =>
    setNominations(n => n.map((row, idx) =>
      idx === mi ? row.filter((_, ridx) => ridx !== ni) : row
    ));
  const updateNomination = (mi, ni, field, val) =>
    setNominations(n => n.map((row, idx) =>
      idx === mi ? row.map((nom, ridx) => ridx === ni ? { ...nom, [field]: val } : nom) : row
    ));

  const addEvent = () => setEvents(e => [...e, emptyEvent()]);
  const removeEvent = (i) => { if (events.length > 1) setEvents(e => e.filter((_, idx) => idx !== i)); };
  const updateEvent = (i, field, val) =>
    setEvents(e => e.map((ev, idx) => idx === i ? { ...ev, [field]: val } : ev));

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!fy) return toast.error('Please enter the financial year');
    try {
      setSubmitting(true);
      await clientPortalAPI.startAudit({
        financial_year: fy,
        fund_name: fundName,
        date_of_creation: dateOfCreation,
        abn_of_smsf: abn,
        tfn_of_smsf: tfn,
        members,
        trustees,
        bare_trustee: bareTrustee,
        nominations,
        subsequent_events: events,
      });
      onSubmitted?.();
    } catch (err) {
      const msg = err.response?.data?.error || 'Submission failed';
      toast.error(msg);
    } finally {
      setSubmitting(false);
    }
  };

  const inputCls = 'border border-gray-300 rounded-lg px-3 py-2 text-sm w-full focus:outline-none focus:ring-2 focus:ring-blue-500';
  const labelCls = 'block text-xs font-medium text-gray-600 mb-1';

  return (
    <div className="fixed inset-0 z-50 bg-black/40 flex items-start justify-center p-4 overflow-y-auto">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-4xl my-6">
        {/* Header */}
        <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between rounded-t-2xl z-10">
          <div>
            <h2 className="text-lg font-bold text-gray-900">SMSF Basic Data Sheet</h2>
            <p className="text-sm text-gray-500">{entity?.name}</p>
          </div>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
            <XMarkIcon className="h-6 w-6" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-8">

          {/* Fund Details */}
          <section>
            <h3 className="text-sm font-bold text-white bg-[#1A2E5A] px-4 py-2 rounded-lg mb-3">Fund Details</h3>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className={labelCls}>Financial Year *</label>
                <input className={inputCls} value={fy} onChange={e => setFy(e.target.value)}
                  placeholder="e.g. 2024" required />
              </div>
              <div>
                <label className={labelCls}>Name of SMSF</label>
                <input className={inputCls} value={fundName} onChange={e => setFundName(e.target.value)} />
              </div>
              <div>
                <label className={labelCls}>Date of Creation</label>
                <input className={inputCls} type="date" value={dateOfCreation}
                  onChange={e => setDateOfCreation(e.target.value)} />
              </div>
              <div>
                <label className={labelCls}>ABN of SMSF</label>
                <input className={inputCls} value={abn} onChange={e => setAbn(e.target.value)} />
              </div>
              <div>
                <label className={labelCls}>TFN of SMSF</label>
                <input className={inputCls} value={tfn} onChange={e => setTfn(e.target.value)} />
              </div>
            </div>
          </section>

          {/* Members */}
          <section>
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-sm font-bold text-white bg-[#1A2E5A] px-4 py-2 rounded-lg">
                Members ({members.length})
              </h3>
              <button type="button" onClick={addMember}
                className="flex items-center gap-1 text-sm text-[#1B72BE] hover:underline">
                <PlusIcon className="h-4 w-4" /> Add Member
              </button>
            </div>
            {members.map((m, i) => (
              <div key={i} className="border border-gray-200 rounded-lg p-4 mb-3 relative">
                <div className="flex items-center justify-between mb-3">
                  <span className="text-xs font-semibold text-gray-600 bg-blue-100 px-2 py-0.5 rounded">Member {i + 1}</span>
                  {members.length > 1 && (
                    <button type="button" onClick={() => removeMember(i)} className="text-red-400 hover:text-red-600">
                      <TrashIcon className="h-4 w-4" />
                    </button>
                  )}
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <div><label className={labelCls}>Name</label>
                    <input className={inputCls} value={m.name} onChange={e => updateMember(i, 'name', e.target.value)} /></div>
                  <div><label className={labelCls}>Date of Birth</label>
                    <input className={inputCls} type="date" value={m.dob} onChange={e => updateMember(i, 'dob', e.target.value)} /></div>
                  <div className="col-span-2"><label className={labelCls}>Address</label>
                    <textarea className={inputCls} rows={2} value={m.address}
                      onChange={e => updateMember(i, 'address', e.target.value)} /></div>
                  <div><label className={labelCls}>TFN</label>
                    <input className={inputCls} value={m.tfn} onChange={e => updateMember(i, 'tfn', e.target.value)} /></div>
                  <div><label className={labelCls}>Date of Joining</label>
                    <input className={inputCls} type="date" value={m.date_of_joining}
                      onChange={e => updateMember(i, 'date_of_joining', e.target.value)} /></div>
                </div>

                {/* Nominations for this member */}
                <div className="mt-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-medium text-gray-600">Nominations</span>
                    <button type="button" onClick={() => addNomination(i)}
                      className="text-xs text-[#1B72BE] hover:underline flex items-center gap-1">
                      <PlusIcon className="h-3 w-3" /> Add Nominee
                    </button>
                  </div>
                  {(nominations[i] || []).map((nom, ni) => (
                    <div key={ni} className="flex gap-2 mb-2 items-end">
                      <div className="flex-1"><label className={labelCls}>Nominee Name</label>
                        <input className={inputCls} value={nom.nominee}
                          onChange={e => updateNomination(i, ni, 'nominee', e.target.value)} /></div>
                      <div className="w-32"><label className={labelCls}>Relation</label>
                        <input className={inputCls} value={nom.relation}
                          onChange={e => updateNomination(i, ni, 'relation', e.target.value)} /></div>
                      <div className="w-20"><label className={labelCls}>%</label>
                        <input className={inputCls} value={nom.percentage}
                          onChange={e => updateNomination(i, ni, 'percentage', e.target.value)} /></div>
                      {(nominations[i] || []).length > 1 && (
                        <button type="button" onClick={() => removeNomination(i, ni)}
                          className="text-red-400 hover:text-red-600 mb-2">
                          <TrashIcon className="h-4 w-4" />
                        </button>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </section>

          {/* Trustees */}
          <section>
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-sm font-bold text-white bg-[#1A2E5A] px-4 py-2 rounded-lg">
                Trustees ({trustees.length})
              </h3>
              <button type="button" onClick={addTrustee}
                className="flex items-center gap-1 text-sm text-[#1B72BE] hover:underline">
                <PlusIcon className="h-4 w-4" /> Add Trustee
              </button>
            </div>
            {trustees.map((t, i) => (
              <div key={i} className="border border-gray-200 rounded-lg p-4 mb-3">
                <div className="flex items-center justify-between mb-3">
                  <span className="text-xs font-semibold text-gray-600 bg-blue-100 px-2 py-0.5 rounded">Trustee {i + 1}</span>
                  {trustees.length > 1 && (
                    <button type="button" onClick={() => removeTrustee(i)} className="text-red-400 hover:text-red-600">
                      <TrashIcon className="h-4 w-4" />
                    </button>
                  )}
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <div><label className={labelCls}>Name</label>
                    <input className={inputCls} value={t.name} onChange={e => updateTrustee(i, 'name', e.target.value)} /></div>
                  <div><label className={labelCls}>ACN (if Company)</label>
                    <input className={inputCls} value={t.acn} onChange={e => updateTrustee(i, 'acn', e.target.value)} /></div>
                  <div className="col-span-2"><label className={labelCls}>Address</label>
                    <textarea className={inputCls} rows={2} value={t.address}
                      onChange={e => updateTrustee(i, 'address', e.target.value)} /></div>
                </div>
              </div>
            ))}
          </section>

          {/* Bare Trustee */}
          <section>
            <h3 className="text-sm font-bold text-white bg-[#1A2E5A] px-4 py-2 rounded-lg mb-3">Bare Trustee Details</h3>
            <div className="grid grid-cols-2 gap-4">
              <div><label className={labelCls}>Bare Trust Name</label>
                <input className={inputCls} value={bareTrustee.bare_trust_name}
                  onChange={e => setBareTrustee(b => ({ ...b, bare_trust_name: e.target.value }))} /></div>
              <div><label className={labelCls}>Bare Trustee Name</label>
                <input className={inputCls} value={bareTrustee.bare_trustee_name}
                  onChange={e => setBareTrustee(b => ({ ...b, bare_trustee_name: e.target.value }))} /></div>
              <div className="col-span-2"><label className={labelCls}>Address</label>
                <textarea className={inputCls} rows={2} value={bareTrustee.address}
                  onChange={e => setBareTrustee(b => ({ ...b, address: e.target.value }))} /></div>
              <div><label className={labelCls}>ACN (if Company)</label>
                <input className={inputCls} value={bareTrustee.acn}
                  onChange={e => setBareTrustee(b => ({ ...b, acn: e.target.value }))} /></div>
            </div>
          </section>

          {/* Subsequent Events */}
          <section>
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-sm font-bold text-white bg-[#1A2E5A] px-4 py-2 rounded-lg">
                Subsequent Events
              </h3>
              <button type="button" onClick={addEvent}
                className="flex items-center gap-1 text-sm text-[#1B72BE] hover:underline">
                <PlusIcon className="h-4 w-4" /> Add Event
              </button>
            </div>
            {events.map((ev, i) => (
              <div key={i} className="flex gap-3 mb-2 items-end">
                <div className="w-40"><label className={labelCls}>Date</label>
                  <input className={inputCls} type="date" value={ev.date}
                    onChange={e => updateEvent(i, 'date', e.target.value)} /></div>
                <div className="flex-1"><label className={labelCls}>Event Description</label>
                  <input className={inputCls} value={ev.name_of_event}
                    onChange={e => updateEvent(i, 'name_of_event', e.target.value)} /></div>
                {events.length > 1 && (
                  <button type="button" onClick={() => removeEvent(i)}
                    className="text-red-400 hover:text-red-600 mb-2">
                    <TrashIcon className="h-4 w-4" />
                  </button>
                )}
              </div>
            ))}
          </section>

          {/* Footer buttons */}
          <div className="flex justify-end gap-3 pt-4 border-t border-gray-200">
            <button type="button" onClick={onClose}
              className="px-5 py-2.5 border border-gray-300 text-gray-700 rounded-lg text-sm hover:bg-gray-50">
              Cancel
            </button>
            <button type="submit" disabled={submitting}
              className="px-6 py-2.5 bg-[#1B72BE] text-white rounded-lg text-sm font-semibold hover:bg-[#1A2E5A] disabled:opacity-50 transition-colors">
              {submitting ? 'Submitting...' : 'Submit & Generate PDF'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
