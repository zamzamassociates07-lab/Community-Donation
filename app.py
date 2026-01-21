import React, { useState, useEffect, useMemo } from 'react';
import { DonationEntry, DonationCategory, Region } from './types';
import { getDonationInsights } from './services/geminiService';
import ReceiptModal from './components/ReceiptModal';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell, PieChart, Pie } from 'recharts';

const App: React.FC = () => {
  const [entries, setEntries] = useState<DonationEntry[]>([]);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [formData, setFormData] = useState({
    donorName: '',
    amount: '',
    category: DonationCategory.ZAKAT,
    region: Region.AREA_5_NO,
    notes: ''
  });
  const [aiInsight, setAiInsight] = useState<string>('Analyzing donation data...');
  const [loadingInsight, setLoadingInsight] = useState(false);
  const [selectedReceipt, setSelectedReceipt] = useState<DonationEntry | null>(null);

  // Load from LocalStorage
  useEffect(() => {
    const saved = localStorage.getItem('community_donations');
    if (saved) {
      setEntries(JSON.parse(saved));
    }
  }, []);

  useEffect(() => {
    localStorage.setItem('community_donations', JSON.stringify(entries));
    if (entries.length > 0) {
      fetchInsights();
    }
  }, [entries]);

  const fetchInsights = async () => {
    setLoadingInsight(true);
    const insight = await getDonationInsights(entries);
    setAiInsight(insight);
    setLoadingInsight(false);
  };

  const getRegionCode = (region: Region) => {
    switch(region) {
      case Region.AREA_5_NO: return '5N';
      case Region.J_1: return 'J1';
      case Region.J_AREA: return 'JA';
      case Region.AREA_4_NO: return '4N';
      default: return 'GEN';
    }
  };

  const generateReceiptNumber = (region: Region) => {
    const date = new Date();
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const regionCode = getRegionCode(region);
    
    const lastSeq = parseInt(localStorage.getItem('receipt_seq') || '0');
    const nextSeq = lastSeq + 1;
    localStorage.setItem('receipt_seq', nextSeq.toString());
    
    const sequence = String(nextSeq).padStart(7, '0');
    return `${year}${month}${day}-${regionCode}-${sequence}`;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.donorName || !formData.amount) return;

    if (editingId) {
      const updatedEntries = entries.map(entry => {
        if (entry.id === editingId) {
          return {
            ...entry,
            donorName: formData.donorName,
            amount: parseFloat(formData.amount),
            category: formData.category,
            region: formData.region,
            notes: formData.notes
          };
        }
        return entry;
      });
      setEntries(updatedEntries);
      setEditingId(null);
    } else {
      const newEntry: DonationEntry = {
        id: crypto.randomUUID(),
        receiptNumber: generateReceiptNumber(formData.region),
        donorName: formData.donorName,
        amount: parseFloat(formData.amount),
        category: formData.category,
        region: formData.region,
        timestamp: Date.now(),
        notes: formData.notes
      };
      setEntries(prev => [newEntry, ...prev]);
    }

    setFormData({
      donorName: '',
      amount: '',
      category: DonationCategory.ZAKAT,
      region: Region.AREA_5_NO,
      notes: ''
    });
  };

  const handleEdit = (entry: DonationEntry) => {
    setEditingId(entry.id);
    setFormData({
      donorName: entry.donorName,
      amount: entry.amount.toString(),
      category: entry.category,
      region: entry.region,
      notes: entry.notes || ''
    });
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const cancelEdit = () => {
    setEditingId(null);
    setFormData({
      donorName: '',
      amount: '',
      category: DonationCategory.ZAKAT,
      region: Region.AREA_5_NO,
      notes: ''
    });
  };

  const stats = useMemo(() => {
    const total = entries.reduce((sum, e) => sum + e.amount, 0);
    const byCategory = entries.reduce((acc, e) => {
      acc[e.category] = (acc[e.category] || 0) + e.amount;
      return acc;
    }, {} as Record<string, number>);
    const byRegion = entries.reduce((acc, e) => {
      acc[e.region] = (acc[e.region] || 0) + e.amount;
      return acc;
    }, {} as Record<string, number>);

    return { total, byCategory, byRegion };
  }, [entries]);

  const chartData = Object.entries(stats.byCategory).map(([name, value]) => ({ name, value }));
  const regionData = Object.entries(stats.byRegion).map(([name, value]) => ({ name, value }));
  const COLORS = ['#059669', '#2563eb', '#d97706', '#dc2626'];

  return (
    <div className="flex flex-col lg:flex-row min-h-screen bg-[#f1f5f9]">
      {/* Navigation / Sidebar */}
      <aside className="w-full lg:w-[380px] bg-white border-r border-slate-200 lg:h-screen sticky top-0 z-30 flex flex-col">
        <div className="p-8 border-b border-slate-100 flex items-center gap-4">
          <div className="w-12 h-12 bg-emerald-600 rounded-2xl flex items-center justify-center text-white shadow-2xl shadow-emerald-200">
            <i className="fas fa-hand-holding-heart text-2xl"></i>
          </div>
          <div>
            <h1 className="font-black text-emerald-900 leading-none uppercase tracking-tighter text-xl">Donation Hub</h1>
            <span className="text-[10px] text-slate-400 font-bold uppercase tracking-widest mt-1 block">Financial Registry</span>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto p-8 space-y-10">
          <section>
            <h2 className="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em] mb-6 urdu-text flex items-center gap-2">
              <span className="w-1.5 h-1.5 bg-emerald-500 rounded-full"></span>
              {editingId ? 'انٹری میں ترمیم کریں' : 'نئی انٹری درج کریں'}
            </h2>
            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="space-y-1.5">
                <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest flex justify-between px-1">
                  <span>Donor Full Name</span>
                  <span className="urdu-text text-slate-400">نام</span>
                </label>
                <input 
                  type="text" 
                  required
                  placeholder="Ali Ahmed"
                  className="w-full px-5 py-4 bg-slate-50 border border-slate-100 rounded-2xl focus:ring-2 focus:ring-emerald-500 focus:bg-white outline-none transition-all text-sm font-bold placeholder:text-slate-300"
                  value={formData.donorName}
                  onChange={e => setFormData({...formData, donorName: e.target.value})}
                />
              </div>
              
              <div className="space-y-1.5">
                <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest flex justify-between px-1">
                  <span>Amount (PKR)</span>
                  <span className="urdu-text text-slate-400">رقم</span>
                </label>
                <div className="relative">
                  <span className="absolute left-5 top-1/2 -translate-y-1/2 text-slate-400 font-bold text-xs">Rs.</span>
                  <input 
                    type="number" 
                    required
                    placeholder="5000"
                    className="w-full pl-14 pr-5 py-4 bg-slate-50 border border-slate-100 rounded-2xl focus:ring-2 focus:ring-emerald-500 focus:bg-white outline-none transition-all text-sm font-black"
                    value={formData.amount}
                    onChange={e => setFormData({...formData, amount: e.target.value})}
                  />
                </div>
              </div>

              <div className="space-y-1.5">
                <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest flex justify-between px-1">
                  <span>Category</span>
                  <span className="urdu-text text-slate-400">مقصد</span>
                </label>
                <select 
                  className="w-full px-5 py-4 bg-slate-50 border border-slate-100 rounded-2xl focus:ring-2 focus:ring-emerald-500 outline-none transition-all text-sm font-bold appearance-none cursor-pointer"
                  value={formData.category}
                  onChange={e => setFormData({...formData, category: e.target.value as DonationCategory})}
                >
                  {Object.values(DonationCategory).map(c => <option key={c} value={c}>{c}</option>)}
                </select>
              </div>

              <div className="space-y-1.5">
                <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest flex justify-between px-1">
                  <span>Region</span>
                  <span className="urdu-text text-slate-400">علاقہ</span>
                </label>
                <select 
                  className="w-full px-5 py-4 bg-slate-50 border border-slate-100 rounded-2xl focus:ring-2 focus:ring-emerald-500 outline-none transition-all text-sm font-bold appearance-none cursor-pointer"
                  value={formData.region}
                  onChange={e => setFormData({...formData, region: e.target.value as Region})}
                >
                  {Object.values(Region).map(r => <option key={r} value={r}>{r}</option>)}
                </select>
              </div>

              <div className="pt-2">
                <button 
                  type="submit"
                  className={`w-full ${editingId ? 'bg-blue-600 hover:bg-blue-700' : 'bg-emerald-600 hover:bg-emerald-700'} text-white font-black py-5 rounded-[1.5rem] transition-all shadow-xl shadow-emerald-50 flex items-center justify-center gap-3 active:scale-95`}
                >
                  <i className={`fas ${editingId ? 'fa-save' : 'fa-check-double'} text-lg`}></i> 
                  <span className="tracking-widest uppercase text-xs">
                    {editingId ? 'Update Record' : 'Save Entry (محفوظ کریں)'}
                  </span>
                </button>
                {editingId && (
                  <button 
                    type="button"
                    onClick={cancelEdit}
                    className="w-full mt-4 bg-slate-100 text-slate-500 hover:bg-slate-200 font-black py-3 rounded-xl transition-all text-[10px] uppercase tracking-widest"
                  >
                    Cancel Edit
                  </button>
                )}
              </div>
            </form>
          </section>

          <section className="bg-emerald-50 p-6 rounded-[2rem] border border-emerald-100 relative group overflow-hidden">
            <div className="absolute right-0 bottom-0 opacity-5 text-7xl translate-y-4 translate-x-4">
              <i className="fas fa-microchip"></i>
            </div>
            <h3 className="text-[10px] font-black text-emerald-800 uppercase tracking-widest flex items-center gap-2 mb-3">
              <i className="fas fa-sparkles animate-pulse"></i> AI Intelligence Report
            </h3>
            <p className="text-[11px] text-emerald-700 leading-relaxed italic urdu-text">
              {loadingInsight ? 'تجزیہ جاری ہے...' : aiInsight}
            </p>
          </section>
        </div>
      </aside>

      {/* Main Content Dashboard */}
      <main className="flex-1 p-6 lg:p-10 space-y-12 max-w-7xl mx-auto overflow-y-auto">
        <header className="flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="space-y-1">
            <h1 className="text-4xl font-black text-slate-800 tracking-tighter">Community Dashboard</h1>
            <p className="text-slate-400 font-semibold tracking-wide uppercase text-[10px]">Real-time Network Statistics</p>
          </div>
          <div className="flex items-center gap-3 bg-white px-6 py-3 rounded-2xl border border-slate-200 shadow-sm">
             <i className="fas fa-clock text-emerald-600"></i>
             <span className="text-sm font-black text-slate-700">{new Date().toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}</span>
          </div>
        </header>

        {/* Top Metric Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="bg-white p-10 rounded-[2.5rem] border border-slate-200 shadow-sm hover:shadow-xl transition-all group relative overflow-hidden">
             <div className="absolute right-0 top-0 w-24 h-24 bg-emerald-50 rounded-bl-[4rem] flex items-center justify-center -translate-y-2 translate-x-2 group-hover:translate-y-0 group-hover:translate-x-0 transition-transform">
                <i className="fas fa-wallet text-emerald-600 text-2xl"></i>
             </div>
             <p className="text-xs font-black text-slate-400 uppercase tracking-widest mb-2">Total Collection</p>
             <h2 className="text-4xl font-black text-slate-900 tracking-tighter">Rs {stats.total.toLocaleString()}</h2>
          </div>
          <div className="bg-white p-10 rounded-[2.5rem] border border-slate-200 shadow-sm hover:shadow-xl transition-all group relative overflow-hidden">
             <div className="absolute right-0 top-0 w-24 h-24 bg-blue-50 rounded-bl-[4rem] flex items-center justify-center -translate-y-2 translate-x-2 group-hover:translate-y-0 group-hover:translate-x-0 transition-transform">
                <i className="fas fa-receipt text-blue-600 text-2xl"></i>
             </div>
             <p className="text-xs font-black text-slate-400 uppercase tracking-widest mb-2">Verified Receipts</p>
             <h2 className="text-4xl font-black text-slate-900 tracking-tighter">{entries.length}</h2>
          </div>
          <div className="bg-white p-10 rounded-[2.5rem] border border-slate-200 shadow-sm hover:shadow-xl transition-all group relative overflow-hidden">
             <div className="absolute right-0 top-0 w-24 h-24 bg-amber-50 rounded-bl-[4rem] flex items-center justify-center -translate-y-2 translate-x-2 group-hover:translate-y-0 group-hover:translate-x-0 transition-transform">
                <i className="fas fa-hand-holding-heart text-amber-600 text-2xl"></i>
             </div>
             <p className="text-xs font-black text-slate-400 uppercase tracking-widest mb-2">Zakat Component</p>
             <h2 className="text-4xl font-black text-amber-600 tracking-tighter">Rs {(stats.byCategory[DonationCategory.ZAKAT] || 0).toLocaleString()}</h2>
          </div>
        </div>

        {/* Charts and Regional Reporting */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-10">
          <div className="bg-white p-10 rounded-[3rem] border border-slate-200 shadow-sm">
            <h3 className="font-black text-slate-800 mb-10 uppercase text-xs tracking-[0.2em] flex items-center gap-4">
              <span className="w-1.5 h-6 bg-emerald-600 rounded-full"></span>
              Category Distribution
            </h3>
            <div className="h-72">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                  <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{fill: '#94a3b8', fontSize: 10, fontWeight: 'bold'}} />
                  <YAxis axisLine={false} tickLine={false} tick={{fill: '#94a3b8', fontSize: 10}} />
                  <Tooltip cursor={{fill: '#f8fafc'}} contentStyle={{borderRadius: '20px', border: 'none', boxShadow: '0 20px 25px -5px rgb(0 0 0 / 0.1)'}} />
                  <Bar dataKey="value" radius={[12, 12, 0, 0]} barSize={55}>
                    {chartData.map((_, index) => <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />)}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="bg-white p-10 rounded-[3rem] border border-slate-200 shadow-sm flex flex-col">
            <h3 className="font-black text-slate-800 mb-10 uppercase text-xs tracking-[0.2em] flex items-center gap-4">
              <span className="w-1.5 h-6 bg-blue-600 rounded-full"></span>
              Regional Breakdown (علاقائی تفصیلات)
            </h3>
            <div className="flex-1 flex flex-col md:flex-row items-center gap-12">
              <div className="h-56 w-56 shrink-0 relative">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie data={regionData} dataKey="value" nameKey="name" cx="50%" cy="50%" innerRadius={65} outerRadius={85} paddingAngle={10}>
                      {regionData.map((_, index) => <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} stroke="none" />)}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
                <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
                  <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Regions</span>
                  <span className="text-xl font-black text-slate-900">{regionData.length}</span>
                </div>
              </div>
              <div className="flex-1 w-full space-y-4">
                {regionData.length === 0 ? (
                  <p className="text-sm text-slate-400 italic text-center">No regional data available.</p>
                ) : (
                  regionData.map((item, i) => (
                    <div key={item.name} className="flex justify-between items-center p-4 rounded-3xl bg-slate-50 border border-slate-100 group hover:bg-white transition-all cursor-default">
                      <div className="flex items-center gap-4">
                        <div className="w-4 h-4 rounded-full shadow-lg" style={{backgroundColor: COLORS[i % COLORS.length]}}></div>
                        <span className="text-xs font-black text-slate-600 uppercase tracking-widest">{item.name}</span>
                      </div>
                      <span className="text-base font-black text-emerald-600">Rs {item.value.toLocaleString()}</span>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Global Record Log */}
        <div className="bg-white rounded-[3.5rem] border border-slate-200 shadow-sm overflow-hidden mb-16">
          <div className="p-10 border-b border-slate-100 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-6 bg-slate-50/20">
            <div className="flex items-center gap-5">
               <div className="w-14 h-14 bg-emerald-600 text-white rounded-[1.2rem] flex items-center justify-center shadow-2xl shadow-emerald-200">
                 <i className="fas fa-list-check text-xl"></i>
               </div>
               <div>
                  <h3 className="font-black text-slate-800 uppercase tracking-widest text-sm urdu-text leading-none">ڈونیشن ریکارڈ لاگ</h3>
                  <p className="text-[10px] text-slate-400 font-bold uppercase tracking-widest mt-1">Immutable Transaction History</p>
               </div>
            </div>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left">
              <thead>
                <tr className="text-[10px] font-black text-slate-400 uppercase tracking-[0.3em] bg-slate-50/50 border-b border-slate-100">
                  <th className="px-10 py-6">ID Code</th>
                  <th className="px-10 py-6">Donor Information</th>
                  <th className="px-10 py-6">Purpose</th>
                  <th className="px-10 py-6">Region</th>
                  <th className="px-10 py-6">Amount</th>
                  <th className="px-10 py-6 text-center">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {entries.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="px-10 py-32 text-center text-slate-400 italic text-sm">
                       <i className="fas fa-database text-6xl block mb-6 opacity-10"></i>
                       No active transactions found in the cloud ledger.
                    </td>
                  </tr>
                ) : (
                  entries.map(entry => (
                    <tr key={entry.id} className="hover:bg-slate-50/50 transition-all group">
                      <td className="px-10 py-6">
                        <span className="font-mono font-black text-emerald-600 text-[11px] tracking-tighter bg-emerald-50 px-3 py-1.5 rounded-lg border border-emerald-100">{entry.receiptNumber}</span>
                      </td>
                      <td className="px-10 py-6">
                         <div className="font-black text-slate-800 text-base">{entry.donorName}</div>
                         <div className="text-[10px] text-slate-400 font-bold uppercase mt-1 flex items-center gap-2">
                           <i className="fas fa-calendar-check text-[8px]"></i>
                           {new Date(entry.timestamp).toLocaleString([], {day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute:'2-digit'})}
                         </div>
                      </td>
                      <td className="px-10 py-6">
                        <span className="bg-slate-100 text-slate-500 px-4 py-2 rounded-xl text-[9px] font-black uppercase tracking-widest border border-slate-200">{entry.category}</span>
                      </td>
                      <td className="px-10 py-6">
                        <div className="text-[11px] font-black text-slate-400 uppercase tracking-widest border-l-2 border-slate-200 pl-3">{entry.region}</div>
                      </td>
                      <td className="px-10 py-6 font-black text-slate-900 text-lg">Rs {entry.amount.toLocaleString()}</td>
                      <td className="px-10 py-6">
                        <div className="flex justify-center gap-4">
                          <button 
                            onClick={() => setSelectedReceipt(entry)}
                            className="bg-emerald-600 text-white hover:bg-emerald-700 px-6 py-3 rounded-2xl text-[10px] font-black uppercase tracking-widest transition-all shadow-xl shadow-emerald-50 flex items-center gap-3 group-hover:scale-105 active:scale-95"
                          >
                            <i className="fas fa-print"></i> Receipt
                          </button>
                          <button 
                            onClick={() => handleEdit(entry)}
                            className="bg-white text-blue-600 border border-slate-200 hover:border-blue-600 hover:bg-blue-600 hover:text-white w-12 h-12 rounded-2xl transition-all flex items-center justify-center group-hover:scale-105 active:scale-95 shadow-sm"
                          >
                            <i className="fas fa-pencil-alt text-sm"></i>
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </main>

      {/* The Printable Receipt Modal */}
      {selectedReceipt && (
        <ReceiptModal 
          entry={selectedReceipt} 
          onClose={() => setSelectedReceipt(null)} 
        />
      )}
    </div>
  );
};

export default App;
