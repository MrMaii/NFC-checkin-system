import React, { useState, useEffect, useMemo } from 'react';
import { motion, AnimatePresence, LayoutGroup } from 'framer-motion';
import { 
  LogIn, LogOut, Clock, ShieldCheck, AlertCircle, 
  Mail, Hash, Moon, Sun, Monitor,
  Activity, Users, UserMinus, UserCheck, Search
} from 'lucide-react';

// --- 配置与翻译 ---
// 部署到公网服务器时，把下面地址改成你的服务器地址:
// 例如：const API_BASE = "https://your-domain.com" 或 "http://你的服务器IP:5000"
const API_BASE = "http://112.126.57.41:5000";

const API_GET_URL = `${API_BASE}/get_status`;
const API_UPDATE_URL = `${API_BASE}/update`;

const TRANSLATIONS = {
  zh: {
    title: "宿舍指挥中心",
    subtitle: "宿舍登陆情况监控系统",
    inside: "在宿人员",
    outside: "离宿人员",
    total: "总人数",
    room: "房号",
    lastCheck: "最近同步",
    statusError: "链路中断",
    search: "搜索姓名或房号...",
    footer: "加密传输协议 v3.8 // 实时网格追踪系统 // 授权终端",
    langName: "EN"
  },
  en: {
    title: "NCA RA Command Center",
    subtitle: "Residence sign Tracking System",
    inside: "On Premises",
    outside: "Off Premises",
    total: "Total Records",
    room: "Unit",
    lastCheck: "Last Sync",
    statusError: "Link Severed",
    search: "Search name or unit...",
    footer: "ENCRYPTED PROTOCOL v3.8 // REAL-TIME GRID TRACKING // AUTHORIZED ONLY",
    langName: "中文"
  }
};

const springTransition = {
  type: "spring",
  stiffness: 450,
  damping: 35,
  mass: 0.8
};

const App = () => {
  const [students, setStudents] = useState({});
  const [error, setError] = useState(null);
  const [lang, setLang] = useState('zh');
  const [themeMode, setThemeMode] = useState('dark');
  const [resolvedTheme, setResolvedTheme] = useState('dark');
  const [searchQuery, setSearchQuery] = useState('');

  const t = TRANSLATIONS[lang];

  useEffect(() => {
    const handleTheme = () => {
      if (themeMode === 'system') {
        const isDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        setResolvedTheme(isDark ? 'dark' : 'light');
      } else {
        setResolvedTheme(themeMode);
      }
    };
    handleTheme();
    const mq = window.matchMedia('(prefers-color-scheme: dark)');
    mq.addEventListener('change', handleTheme);
    return () => mq.removeEventListener('change', handleTheme);
  }, [themeMode]);

  const fetchData = async () => {
    try {
      const res = await fetch(API_GET_URL);
      if (!res.ok) throw new Error();
      const data = await res.json();
      setStudents(data);
      setError(null);
    } catch (err) {
      setError(t.statusError);
    }
  };

  useEffect(() => {
    fetchData();
    const timer = setInterval(fetchData, 1000); 
    return () => clearInterval(timer);
  }, [t.statusError]);

  const updateStudentStatus = async (name, newStatus) => {
    setStudents(prev => ({
      ...prev,
      [name]: { ...prev[name], status: newStatus }
    }));

    try {
      await fetch(API_UPDATE_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, status: newStatus }),
      });
    } catch (err) {
      console.warn("Sync failed, but keeping local optimistic state");
    }
  };

  const studentList = useMemo(() => {
    return Object.values(students).filter(s => 
      s.name.toLowerCase().includes(searchQuery.toLowerCase()) || 
      s.room.includes(searchQuery)
    );
  }, [students, searchQuery]);

  const inside = studentList.filter(s => s.status === 1);
  const outside = studentList.filter(s => s.status === 0);

  const themeStyles = resolvedTheme === 'dark' 
    ? "bg-[#05070a] text-slate-200" 
    : "bg-slate-50 text-slate-900";

  return (
    <div className={`min-h-screen transition-colors duration-700 ${themeStyles} font-sans overflow-x-hidden`}>
      <div className="max-w-[1600px] mx-auto p-4 md:p-8">
        <header className="flex flex-col xl:flex-row justify-between items-start xl:items-center gap-6 mb-12">
          <div className="flex items-center gap-5">
            <div className={`p-4 rounded-2xl shadow-xl transition-colors ${resolvedTheme === 'dark' ? 'bg-cyan-500/10 border border-cyan-500/20' : 'bg-white border border-slate-200'}`}>
              <ShieldCheck className={`w-8 h-8 ${resolvedTheme === 'dark' ? 'text-cyan-400' : 'text-blue-600'}`} />
            </div>
            <div>
              <h1 className="text-4xl font-black tracking-tighter uppercase italic leading-none flex items-center gap-3">
                {t.title} <span className="text-xs not-italic font-mono bg-blue-500 text-white px-2 py-0.5 rounded-full tracking-widest">PRO</span>
              </h1>
              <p className="text-slate-500 text-xs font-bold tracking-[0.2em] mt-2 uppercase flex items-center gap-2">
                <Activity className="w-3 h-3 animate-pulse" /> {t.subtitle}
              </p>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-4 w-full xl:w-auto">
            <div className="relative flex-grow xl:flex-grow-0">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
              <input 
                type="text" placeholder={t.search} value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className={`w-full xl:w-64 pl-11 pr-4 py-3 rounded-2xl text-sm border outline-none transition-all ${
                  resolvedTheme === 'dark' ? 'bg-slate-900/50 border-white/5 focus:border-cyan-500' : 'bg-white border-slate-200 focus:border-blue-500 shadow-sm'
                }`}
              />
            </div>
            <div className="flex items-center gap-2 bg-slate-100 dark:bg-slate-900/80 p-1.5 rounded-2xl border dark:border-white/5">
              <button onClick={() => setLang(lang === 'zh' ? 'en' : 'zh')} className="px-4 py-2 text-xs font-black uppercase hover:bg-white dark:hover:bg-slate-800 rounded-xl transition-all">
                {t.langName}
              </button>
              <div className="flex gap-1">
                {[{ id: 'light', icon: Sun }, { id: 'dark', icon: Moon }, { id: 'system', icon: Monitor }].map(({ id, icon: Icon }) => (
                  <button key={id} onClick={() => setThemeMode(id)} className={`p-2 rounded-xl transition-colors ${themeMode === id ? 'bg-white dark:bg-slate-700 text-blue-500 shadow-sm' : 'text-slate-400 hover:text-slate-200'}`}>
                    <Icon className="w-4 h-4" />
                  </button>
                ))}
              </div>
            </div>
          </div>
        </header>

        <section className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-12">
          <StatCard label={t.inside} value={inside.length} icon={UserCheck} color="cyan" theme={resolvedTheme} />
          <StatCard label={t.outside} value={outside.length} icon={UserMinus} color="rose" theme={resolvedTheme} />
          <StatCard label={t.total} value={studentList.length} icon={Users} color="indigo" theme={resolvedTheme} />
          <StatCard label="Network" value={error ? "ERR" : "OK"} icon={Activity} color={error ? "rose" : "emerald"} theme={resolvedTheme} />
        </section>

        <LayoutGroup>
          <main className="grid grid-cols-1 xl:grid-cols-2 gap-10">
            <StatusColumn 
              title={t.inside} students={inside} color="cyan" t={t} theme={resolvedTheme} 
              onMove={(name) => updateStudentStatus(name, 0)} // 在宿 -> 离宿 (Status 0)
            />
            <StatusColumn 
              title={t.outside} students={outside} color="rose" t={t} theme={resolvedTheme} 
              onMove={(name) => updateStudentStatus(name, 1)} // 离宿 -> 在宿 (Status 1)
            />
          </main>
        </LayoutGroup>

        <footer className="mt-20 py-8 border-t dark:border-white/5 opacity-40 text-[10px] uppercase font-black tracking-[0.4em] flex justify-between">
          <span>{t.footer}</span>
          <span>DCC_TERMINAL_ACTIVE // {new Date().toLocaleTimeString()}</span>
        </footer>
      </div>
    </div>
  );
};

const StatCard = ({ label, value, icon: Icon, color, theme }) => {
  const colors = {
    cyan: "text-cyan-500 bg-cyan-500/10",
    rose: "text-rose-500 bg-rose-500/10",
    indigo: "text-indigo-500 bg-indigo-500/10",
    emerald: "text-emerald-500 bg-emerald-500/10"
  };
  return (
    <div className={`p-5 rounded-3xl border transition-all ${theme === 'dark' ? 'bg-slate-900/40 border-white/5' : 'bg-white border-slate-200 shadow-sm'}`}>
      <div className="flex justify-between mb-4">
        <div className={`p-2 rounded-xl ${colors[color]}`}><Icon className="w-5 h-5" /></div>
        <span className="text-[10px] font-black uppercase opacity-40 tracking-widest">{label}</span>
      </div>
      <span className="text-3xl font-black tracking-tighter">{value}</span>
    </div>
  );
};

const StatusColumn = ({ title, students, color, t, theme, onMove }) => (
  <section className="flex flex-col gap-6">
    <div className="flex items-center gap-4 px-2">
      <div className={`w-2 h-8 rounded-full ${color === 'cyan' ? 'bg-cyan-500 shadow-[0_0_15px_rgba(6,182,212,0.5)]' : 'bg-rose-500 shadow-[0_0_15px_rgba(244,63,94,0.5)]'}`} />
      <h2 className="text-2xl font-black uppercase tracking-tighter italic transition-all">{title} <span className="opacity-30">[{students.length}]</span></h2>
    </div>
    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 min-h-[400px]">
      <AnimatePresence mode="popLayout" initial={false}>
        {students.map((s) => (
          <StudentCard key={s.name} student={s} t={t} theme={theme} color={color} onMove={onMove} />
        ))}
      </AnimatePresence>
    </div>
  </section>
);

const StudentCard = ({ student, t, theme, color, onMove }) => {
  const isDark = theme === 'dark';
  
  return (
    <motion.div
      layoutId={student.name}
      layout
      transition={springTransition}
      drag // 允许全方向自由拖拽
      dragConstraints={{ left: 0, right: 0, top: 0, bottom: 0 }} // 配合 dragElastic 实现随鼠标移动并回弹
      dragElastic={0.9} // 极高弹性，确保卡片紧紧跟随鼠标
      onDragEnd={(e, info) => {
        const xThreshold = 140; // 左右判定阈值
        const yThreshold = 100; // 上下判定辅助（可选）
        
        // 双向判定逻辑
        // 1. 如果当前是“在宿(cyan)”，向右拖拽超过阈值 -> 移动
        if (color === 'cyan' && info.offset.x > xThreshold) {
          onMove(student.name);
        }
        // 2. 如果当前是“离宿(rose)”，向左拖拽超过阈值 -> 移动
        else if (color === 'rose' && info.offset.x < -xThreshold) {
          onMove(student.name);
        }
      }}
      whileDrag={{ 
        scale: 1.08, 
        zIndex: 100, 
        cursor: 'grabbing',
        boxShadow: isDark ? "0 20px 40px rgba(0,0,0,0.6)" : "0 20px 40px rgba(0,0,0,0.15)"
      }}
      whileTap={{ scale: 0.96 }}
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.8, transition: { duration: 0.2 } }}
      className={`relative p-5 rounded-[2rem] border cursor-grab transition-colors active:shadow-2xl ${
        isDark ? 'bg-slate-900/80 border-white/5 hover:border-white/20' : 'bg-white border-slate-200 shadow-md hover:shadow-xl'
      }`}
    >
      <div className="flex justify-between items-start mb-6">
        <div className="flex items-center gap-4">
          <div className={`w-14 h-14 rounded-2xl flex items-center justify-center font-black text-xl text-white ${color === 'cyan' ? 'bg-cyan-500' : 'bg-rose-500'} shadow-inner`}>
            {student.name.charAt(0)}
          </div>
          <div>
            <h3 className="text-lg font-black tracking-tight">{student.name}</h3>
            <span className="text-[9px] font-black uppercase tracking-[0.2em] opacity-40">
              {student.status === 1 ? 'Stationary' : 'Away'}
            </span>
          </div>
        </div>
        <div className={`font-mono text-[10px] font-black px-2.5 py-1 rounded-lg border ${isDark ? 'bg-black/40 border-white/5 text-cyan-400' : 'bg-slate-100 border-slate-200 text-slate-500'}`}>
          UNIT-{student.room}
        </div>
      </div>
      
      <div className={`space-y-3 p-4 rounded-2xl border transition-colors ${isDark ? 'bg-black/30 border-white/5' : 'bg-slate-50 border-slate-100'}`}>
        <div className="flex items-center gap-3 text-xs opacity-70 italic truncate">
          <Mail className="w-3.5 h-3.5 flex-shrink-0" />
          {student.email}
        </div>
        <div className="flex items-center gap-3 text-xs font-bold opacity-70">
          <Hash className="w-3.5 h-3.5" />
          {t.room}: {student.room}
        </div>
      </div>

      <div className="mt-5 flex items-center gap-2 opacity-30 text-[9px] font-mono font-bold italic">
        <Clock className="w-3 h-3" /> {t.lastCheck}: {student.last_update}
      </div>

      {/* 拖拽指示增强（仅拖拽时显示） */}
      <motion.div 
        className="absolute inset-0 rounded-[2rem] pointer-events-none border-2 border-dashed border-white/20 opacity-0"
        whileDrag={{ opacity: 1 }}
      />
    </motion.div>
  );
};

export default App;