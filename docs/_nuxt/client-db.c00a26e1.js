import{a3 as $,O as P,a4 as U,W as Y}from"./entry.532d491b.js";import{g as W,a as _,b as E,s as T,c as M,w as B,d as b,f as J}from"./query.921812c6.js";import{p as H}from"./index.a6ef77ff.js";import{u as L}from"./preview.809672a4.js";import"./utils.10201b9d.js";const q="memory",k=()=>{const r=new Map;return{name:q,options:{},hasItem(t){return r.has(t)},getItem(t){return r.get(t)||null},getItemRaw(t){return r.get(t)||null},setItem(t,n){r.set(t,n)},setItemRaw(t,n){r.set(t,n)},removeItem(t){r.delete(t)},getKeys(){return Array.from(r.keys())},clear(){r.clear()},dispose(){r.clear()}}};function G(r){return!r||typeof r.then!="function"?Promise.resolve(r):r}function p(r,...t){try{return G(r(...t))}catch(n){return Promise.reject(n)}}function Z(r){const t=typeof r;return r===null||t!=="object"&&t!=="function"}function F(r){const t=Object.getPrototypeOf(r);return!t||t.isPrototypeOf(Object)}function S(r){if(Z(r))return String(r);if(F(r)||Array.isArray(r))return JSON.stringify(r);if(typeof r.toJSON=="function")return S(r.toJSON());throw new Error("[unstorage] Cannot stringify value!")}function N(){if(typeof Buffer===void 0)throw new TypeError("[unstorage] Buffer is not supported!")}const R="base64:";function V(r){if(typeof r=="string")return r;N();const t=Buffer.from(r).toString("base64");return R+t}function Q(r){return typeof r!="string"||!r.startsWith(R)?r:(N(),Buffer.from(r.slice(R.length),"base64"))}const X=["hasItem","getItem","getItemRaw","setItem","setItemRaw","removeItem","getMeta","setMeta","removeMeta","getKeys","clear","mount","unmount"];function ee(r,t){if(t=A(t),!t)return r;const n={...r};for(const a of X)n[a]=(o="",...u)=>r[a](t+o,...u);return n.getKeys=(a="",...o)=>r.getKeys(t+a,...o).then(u=>u.map(f=>f.slice(t.length))),n}function d(r){return r?r.split("?")[0].replace(/[/\\]/g,":").replace(/:+/g,":").replace(/^:|:$/g,""):""}function te(...r){return d(r.join(":"))}function A(r){return r=d(r),r?r+":":""}const re="memory",ne=()=>{const r=new Map;return{name:re,options:{},hasItem(t){return r.has(t)},getItem(t){return r.get(t)||null},getItemRaw(t){return r.get(t)||null},setItem(t,n){r.set(t,n)},setItemRaw(t,n){r.set(t,n)},removeItem(t){r.delete(t)},getKeys(){return Array.from(r.keys())},clear(){r.clear()},dispose(){r.clear()}}};function ie(r={}){const t={mounts:{"":r.driver||ne()},mountpoints:[""],watching:!1,watchListeners:[],unwatch:{}},n=e=>{for(const i of t.mountpoints)if(e.startsWith(i))return{base:i,relativeKey:e.slice(i.length),driver:t.mounts[i]};return{base:"",relativeKey:e,driver:t.mounts[""]}},a=(e,i)=>t.mountpoints.filter(s=>s.startsWith(e)||i&&e.startsWith(s)).map(s=>({relativeBase:e.length>s.length?e.slice(s.length):void 0,mountpoint:s,driver:t.mounts[s]})),o=(e,i)=>{if(t.watching){i=d(i);for(const s of t.watchListeners)s(e,i)}},u=async()=>{if(!t.watching){t.watching=!0;for(const e in t.mounts)t.unwatch[e]=await C(t.mounts[e],o,e)}},f=async()=>{if(t.watching){for(const e in t.unwatch)await t.unwatch[e]();t.unwatch={},t.watching=!1}},h=(e,i,s)=>{const c=new Map,l=m=>{let y=c.get(m.base);return y||(y={driver:m.driver,base:m.base,items:[]},c.set(m.base,y)),y};for(const m of e){const y=typeof m=="string",v=d(y?m:m.key),w=y?void 0:m.value,I=y||!m.options?i:{...i,...m.options},O=n(v);l(O).items.push({key:v,value:w,relativeKey:O.relativeKey,options:I})}return Promise.all([...c.values()].map(m=>s(m))).then(m=>m.flat())},g={hasItem(e,i={}){e=d(e);const{relativeKey:s,driver:c}=n(e);return p(c.hasItem,s,i)},getItem(e,i={}){e=d(e);const{relativeKey:s,driver:c}=n(e);return p(c.getItem,s,i).then(l=>$(l))},getItems(e,i){return h(e,i,s=>s.driver.getItems?p(s.driver.getItems,s.items.map(c=>({key:c.relativeKey,options:c.options})),i).then(c=>c.map(l=>({key:te(s.base,l.key),value:$(l.value)}))):Promise.all(s.items.map(c=>p(s.driver.getItem,c.relativeKey,c.options).then(l=>({key:c.key,value:$(l)})))))},getItemRaw(e,i={}){e=d(e);const{relativeKey:s,driver:c}=n(e);return c.getItemRaw?p(c.getItemRaw,s,i):p(c.getItem,s,i).then(l=>Q(l))},async setItem(e,i,s={}){if(i===void 0)return g.removeItem(e);e=d(e);const{relativeKey:c,driver:l}=n(e);l.setItem&&(await p(l.setItem,c,S(i),s),l.watch||o("update",e))},async setItems(e,i){await h(e,i,async s=>{s.driver.setItems&&await p(s.driver.setItems,s.items.map(c=>({key:c.relativeKey,value:S(c.value),options:c.options})),i),s.driver.setItem&&await Promise.all(s.items.map(c=>p(s.driver.setItem,c.relativeKey,S(c.value),c.options)))})},async setItemRaw(e,i,s={}){if(i===void 0)return g.removeItem(e,s);e=d(e);const{relativeKey:c,driver:l}=n(e);if(l.setItemRaw)await p(l.setItemRaw,c,i,s);else if(l.setItem)await p(l.setItem,c,V(i),s);else return;l.watch||o("update",e)},async removeItem(e,i={}){typeof i=="boolean"&&(i={removeMeta:i}),e=d(e);const{relativeKey:s,driver:c}=n(e);c.removeItem&&(await p(c.removeItem,s,i),(i.removeMeta||i.removeMata)&&await p(c.removeItem,s+"$",i),c.watch||o("remove",e))},async getMeta(e,i={}){typeof i=="boolean"&&(i={nativeOnly:i}),e=d(e);const{relativeKey:s,driver:c}=n(e),l=Object.create(null);if(c.getMeta&&Object.assign(l,await p(c.getMeta,s,i)),!i.nativeOnly){const m=await p(c.getItem,s+"$",i).then(y=>$(y));m&&typeof m=="object"&&(typeof m.atime=="string"&&(m.atime=new Date(m.atime)),typeof m.mtime=="string"&&(m.mtime=new Date(m.mtime)),Object.assign(l,m))}return l},setMeta(e,i,s={}){return this.setItem(e+"$",i,s)},removeMeta(e,i={}){return this.removeItem(e+"$",i)},async getKeys(e,i={}){e=A(e);const s=a(e,!0);let c=[];const l=[];for(const m of s){const v=(await p(m.driver.getKeys,m.relativeBase,i)).map(w=>m.mountpoint+d(w)).filter(w=>!c.some(I=>w.startsWith(I)));l.push(...v),c=[m.mountpoint,...c.filter(w=>!w.startsWith(m.mountpoint))]}return e?l.filter(m=>m.startsWith(e)&&!m.endsWith("$")):l.filter(m=>!m.endsWith("$"))},async clear(e,i={}){e=A(e),await Promise.all(a(e,!1).map(async s=>{if(s.driver.clear)return p(s.driver.clear,s.relativeBase,i);if(s.driver.removeItem){const c=await s.driver.getKeys(s.relativeBase||"",i);return Promise.all(c.map(l=>s.driver.removeItem(l,i)))}}))},async dispose(){await Promise.all(Object.values(t.mounts).map(e=>x(e)))},async watch(e){return await u(),t.watchListeners.push(e),async()=>{t.watchListeners=t.watchListeners.filter(i=>i!==e),t.watchListeners.length===0&&await f()}},async unwatch(){t.watchListeners=[],await f()},mount(e,i){if(e=A(e),e&&t.mounts[e])throw new Error(`already mounted at ${e}`);return e&&(t.mountpoints.push(e),t.mountpoints.sort((s,c)=>c.length-s.length)),t.mounts[e]=i,t.watching&&Promise.resolve(C(i,o,e)).then(s=>{t.unwatch[e]=s}).catch(console.error),g},async unmount(e,i=!0){e=A(e),!(!e||!t.mounts[e])&&(t.watching&&e in t.unwatch&&(t.unwatch[e](),delete t.unwatch[e]),i&&await x(t.mounts[e]),t.mountpoints=t.mountpoints.filter(s=>s!==e),delete t.mounts[e])},getMount(e=""){e=d(e)+":";const i=n(e);return{driver:i.driver,base:i.base}},getMounts(e="",i={}){return e=d(e),a(e,i.parents).map(c=>({driver:c.driver,base:c.mountpoint}))}};return g}function C(r,t,n){return r.watch?r.watch((a,o)=>t(a,n+o)):()=>{}}async function x(r){typeof r.dispose=="function"&&await p(r.dispose)}function ae(r={}){const t=se(n,r.operators);function n(a,o){return typeof o!="object"||o instanceof RegExp?t.$eq(a,o):Object.keys(o||{}).every(u=>{const f=o[u];if(u.startsWith("$")&&t[u]){const h=t[u];return typeof h=="function"?h(a,f):!1}return n(W(a,u),f)})}return n}function se(r,t={}){return{$match:(n,a)=>r(n,a),$eq:(n,a)=>a instanceof RegExp?a.test(n):n===a,$ne:(n,a)=>a instanceof RegExp?!a.test(n):n!==a,$not:(n,a)=>!r(n,a),$and:(n,a)=>(_(a,"$and requires an array as condition"),a.every(o=>r(n,o))),$or:(n,a)=>(_(a,"$or requires an array as condition"),a.some(o=>r(n,o))),$in:(n,a)=>E(a).some(o=>Array.isArray(n)?r(n,{$contains:o}):r(n,o)),$contains:(n,a)=>(n=Array.isArray(n)?n:String(n),E(a).every(o=>n.includes(o))),$icontains:(n,a)=>{if(typeof a!="string")throw new TypeError("$icontains requires a string, use $contains instead");return n=String(n).toLocaleLowerCase(),E(a).every(o=>n.includes(o.toLocaleLowerCase()))},$containsAny:(n,a)=>(_(a,"$containsAny requires an array as condition"),n=Array.isArray(n)?n:String(n),a.some(o=>n.includes(o))),$exists:(n,a)=>a?typeof n<"u":typeof n>"u",$type:(n,a)=>typeof n===String(a),$regex:(n,a)=>{if(!(a instanceof RegExp)){const o=String(a).match(/\/(.*)\/([dgimsuy]*)$/);a=o?new RegExp(o[1],o[2]||""):new RegExp(a)}return a.test(String(n||""))},$lt:(n,a)=>n<a,$lte:(n,a)=>n<=a,$gt:(n,a)=>n>a,$gte:(n,a)=>n>=a,...t||{}}}function D(r){const t=ae(),n=(o,{query:u,before:f,after:h})=>{const g=typeof u=="string"?{_path:u}:u,e=o.findIndex(s=>t(s,g));f=f??1,h=h??1;const i=new Array(f+h).fill(null,0);return e===-1?i:i.map((s,c)=>o[e-f+c+ +(c>=f)]||null)},a=[(o,u)=>o.filter(f=>E(u.where).every(h=>t(f,h))),(o,u)=>E(u.sort).forEach(f=>T(o,f)),(o,u)=>u.surround?n(o,u.surround):o,(o,u)=>u.skip?o.slice(u.skip):o,(o,u)=>u.limit?o.slice(0,u.limit):o,(o,u)=>M(B(u.without))(o),(o,u)=>M(b(u.only))(o)];return async o=>{const u=await r(),f=o.params(),h=a.reduce((g,e)=>e(g,f)||g,u);return f.first?h[0]:h}}var oe=typeof globalThis<"u"?globalThis:typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{},ue={exports:{}};(function(r,t){(function(n,a,o){r.exports=o(),r.exports.default=o()})("slugify",oe,function(){var n=JSON.parse(`{"$":"dollar","%":"percent","&":"and","<":"less",">":"greater","|":"or","¢":"cent","£":"pound","¤":"currency","¥":"yen","©":"(c)","ª":"a","®":"(r)","º":"o","À":"A","Á":"A","Â":"A","Ã":"A","Ä":"A","Å":"A","Æ":"AE","Ç":"C","È":"E","É":"E","Ê":"E","Ë":"E","Ì":"I","Í":"I","Î":"I","Ï":"I","Ð":"D","Ñ":"N","Ò":"O","Ó":"O","Ô":"O","Õ":"O","Ö":"O","Ø":"O","Ù":"U","Ú":"U","Û":"U","Ü":"U","Ý":"Y","Þ":"TH","ß":"ss","à":"a","á":"a","â":"a","ã":"a","ä":"a","å":"a","æ":"ae","ç":"c","è":"e","é":"e","ê":"e","ë":"e","ì":"i","í":"i","î":"i","ï":"i","ð":"d","ñ":"n","ò":"o","ó":"o","ô":"o","õ":"o","ö":"o","ø":"o","ù":"u","ú":"u","û":"u","ü":"u","ý":"y","þ":"th","ÿ":"y","Ā":"A","ā":"a","Ă":"A","ă":"a","Ą":"A","ą":"a","Ć":"C","ć":"c","Č":"C","č":"c","Ď":"D","ď":"d","Đ":"DJ","đ":"dj","Ē":"E","ē":"e","Ė":"E","ė":"e","Ę":"e","ę":"e","Ě":"E","ě":"e","Ğ":"G","ğ":"g","Ģ":"G","ģ":"g","Ĩ":"I","ĩ":"i","Ī":"i","ī":"i","Į":"I","į":"i","İ":"I","ı":"i","Ķ":"k","ķ":"k","Ļ":"L","ļ":"l","Ľ":"L","ľ":"l","Ł":"L","ł":"l","Ń":"N","ń":"n","Ņ":"N","ņ":"n","Ň":"N","ň":"n","Ō":"O","ō":"o","Ő":"O","ő":"o","Œ":"OE","œ":"oe","Ŕ":"R","ŕ":"r","Ř":"R","ř":"r","Ś":"S","ś":"s","Ş":"S","ş":"s","Š":"S","š":"s","Ţ":"T","ţ":"t","Ť":"T","ť":"t","Ũ":"U","ũ":"u","Ū":"u","ū":"u","Ů":"U","ů":"u","Ű":"U","ű":"u","Ų":"U","ų":"u","Ŵ":"W","ŵ":"w","Ŷ":"Y","ŷ":"y","Ÿ":"Y","Ź":"Z","ź":"z","Ż":"Z","ż":"z","Ž":"Z","ž":"z","Ə":"E","ƒ":"f","Ơ":"O","ơ":"o","Ư":"U","ư":"u","ǈ":"LJ","ǉ":"lj","ǋ":"NJ","ǌ":"nj","Ș":"S","ș":"s","Ț":"T","ț":"t","ə":"e","˚":"o","Ά":"A","Έ":"E","Ή":"H","Ί":"I","Ό":"O","Ύ":"Y","Ώ":"W","ΐ":"i","Α":"A","Β":"B","Γ":"G","Δ":"D","Ε":"E","Ζ":"Z","Η":"H","Θ":"8","Ι":"I","Κ":"K","Λ":"L","Μ":"M","Ν":"N","Ξ":"3","Ο":"O","Π":"P","Ρ":"R","Σ":"S","Τ":"T","Υ":"Y","Φ":"F","Χ":"X","Ψ":"PS","Ω":"W","Ϊ":"I","Ϋ":"Y","ά":"a","έ":"e","ή":"h","ί":"i","ΰ":"y","α":"a","β":"b","γ":"g","δ":"d","ε":"e","ζ":"z","η":"h","θ":"8","ι":"i","κ":"k","λ":"l","μ":"m","ν":"n","ξ":"3","ο":"o","π":"p","ρ":"r","ς":"s","σ":"s","τ":"t","υ":"y","φ":"f","χ":"x","ψ":"ps","ω":"w","ϊ":"i","ϋ":"y","ό":"o","ύ":"y","ώ":"w","Ё":"Yo","Ђ":"DJ","Є":"Ye","І":"I","Ї":"Yi","Ј":"J","Љ":"LJ","Њ":"NJ","Ћ":"C","Џ":"DZ","А":"A","Б":"B","В":"V","Г":"G","Д":"D","Е":"E","Ж":"Zh","З":"Z","И":"I","Й":"J","К":"K","Л":"L","М":"M","Н":"N","О":"O","П":"P","Р":"R","С":"S","Т":"T","У":"U","Ф":"F","Х":"H","Ц":"C","Ч":"Ch","Ш":"Sh","Щ":"Sh","Ъ":"U","Ы":"Y","Ь":"","Э":"E","Ю":"Yu","Я":"Ya","а":"a","б":"b","в":"v","г":"g","д":"d","е":"e","ж":"zh","з":"z","и":"i","й":"j","к":"k","л":"l","м":"m","н":"n","о":"o","п":"p","р":"r","с":"s","т":"t","у":"u","ф":"f","х":"h","ц":"c","ч":"ch","ш":"sh","щ":"sh","ъ":"u","ы":"y","ь":"","э":"e","ю":"yu","я":"ya","ё":"yo","ђ":"dj","є":"ye","і":"i","ї":"yi","ј":"j","љ":"lj","њ":"nj","ћ":"c","ѝ":"u","џ":"dz","Ґ":"G","ґ":"g","Ғ":"GH","ғ":"gh","Қ":"KH","қ":"kh","Ң":"NG","ң":"ng","Ү":"UE","ү":"ue","Ұ":"U","ұ":"u","Һ":"H","һ":"h","Ә":"AE","ә":"ae","Ө":"OE","ө":"oe","Ա":"A","Բ":"B","Գ":"G","Դ":"D","Ե":"E","Զ":"Z","Է":"E'","Ը":"Y'","Թ":"T'","Ժ":"JH","Ի":"I","Լ":"L","Խ":"X","Ծ":"C'","Կ":"K","Հ":"H","Ձ":"D'","Ղ":"GH","Ճ":"TW","Մ":"M","Յ":"Y","Ն":"N","Շ":"SH","Չ":"CH","Պ":"P","Ջ":"J","Ռ":"R'","Ս":"S","Վ":"V","Տ":"T","Ր":"R","Ց":"C","Փ":"P'","Ք":"Q'","Օ":"O''","Ֆ":"F","և":"EV","ء":"a","آ":"aa","أ":"a","ؤ":"u","إ":"i","ئ":"e","ا":"a","ب":"b","ة":"h","ت":"t","ث":"th","ج":"j","ح":"h","خ":"kh","د":"d","ذ":"th","ر":"r","ز":"z","س":"s","ش":"sh","ص":"s","ض":"dh","ط":"t","ظ":"z","ع":"a","غ":"gh","ف":"f","ق":"q","ك":"k","ل":"l","م":"m","ن":"n","ه":"h","و":"w","ى":"a","ي":"y","ً":"an","ٌ":"on","ٍ":"en","َ":"a","ُ":"u","ِ":"e","ْ":"","٠":"0","١":"1","٢":"2","٣":"3","٤":"4","٥":"5","٦":"6","٧":"7","٨":"8","٩":"9","پ":"p","چ":"ch","ژ":"zh","ک":"k","گ":"g","ی":"y","۰":"0","۱":"1","۲":"2","۳":"3","۴":"4","۵":"5","۶":"6","۷":"7","۸":"8","۹":"9","฿":"baht","ა":"a","ბ":"b","გ":"g","დ":"d","ე":"e","ვ":"v","ზ":"z","თ":"t","ი":"i","კ":"k","ლ":"l","მ":"m","ნ":"n","ო":"o","პ":"p","ჟ":"zh","რ":"r","ს":"s","ტ":"t","უ":"u","ფ":"f","ქ":"k","ღ":"gh","ყ":"q","შ":"sh","ჩ":"ch","ც":"ts","ძ":"dz","წ":"ts","ჭ":"ch","ხ":"kh","ჯ":"j","ჰ":"h","Ṣ":"S","ṣ":"s","Ẁ":"W","ẁ":"w","Ẃ":"W","ẃ":"w","Ẅ":"W","ẅ":"w","ẞ":"SS","Ạ":"A","ạ":"a","Ả":"A","ả":"a","Ấ":"A","ấ":"a","Ầ":"A","ầ":"a","Ẩ":"A","ẩ":"a","Ẫ":"A","ẫ":"a","Ậ":"A","ậ":"a","Ắ":"A","ắ":"a","Ằ":"A","ằ":"a","Ẳ":"A","ẳ":"a","Ẵ":"A","ẵ":"a","Ặ":"A","ặ":"a","Ẹ":"E","ẹ":"e","Ẻ":"E","ẻ":"e","Ẽ":"E","ẽ":"e","Ế":"E","ế":"e","Ề":"E","ề":"e","Ể":"E","ể":"e","Ễ":"E","ễ":"e","Ệ":"E","ệ":"e","Ỉ":"I","ỉ":"i","Ị":"I","ị":"i","Ọ":"O","ọ":"o","Ỏ":"O","ỏ":"o","Ố":"O","ố":"o","Ồ":"O","ồ":"o","Ổ":"O","ổ":"o","Ỗ":"O","ỗ":"o","Ộ":"O","ộ":"o","Ớ":"O","ớ":"o","Ờ":"O","ờ":"o","Ở":"O","ở":"o","Ỡ":"O","ỡ":"o","Ợ":"O","ợ":"o","Ụ":"U","ụ":"u","Ủ":"U","ủ":"u","Ứ":"U","ứ":"u","Ừ":"U","ừ":"u","Ử":"U","ử":"u","Ữ":"U","ữ":"u","Ự":"U","ự":"u","Ỳ":"Y","ỳ":"y","Ỵ":"Y","ỵ":"y","Ỷ":"Y","ỷ":"y","Ỹ":"Y","ỹ":"y","–":"-","‘":"'","’":"'","“":"\\"","”":"\\"","„":"\\"","†":"+","•":"*","…":"...","₠":"ecu","₢":"cruzeiro","₣":"french franc","₤":"lira","₥":"mill","₦":"naira","₧":"peseta","₨":"rupee","₩":"won","₪":"new shequel","₫":"dong","€":"euro","₭":"kip","₮":"tugrik","₯":"drachma","₰":"penny","₱":"peso","₲":"guarani","₳":"austral","₴":"hryvnia","₵":"cedi","₸":"kazakhstani tenge","₹":"indian rupee","₺":"turkish lira","₽":"russian ruble","₿":"bitcoin","℠":"sm","™":"tm","∂":"d","∆":"delta","∑":"sum","∞":"infinity","♥":"love","元":"yuan","円":"yen","﷼":"rial","ﻵ":"laa","ﻷ":"laa","ﻹ":"lai","ﻻ":"la"}`),a=JSON.parse('{"bg":{"Й":"Y","Ц":"Ts","Щ":"Sht","Ъ":"A","Ь":"Y","й":"y","ц":"ts","щ":"sht","ъ":"a","ь":"y"},"de":{"Ä":"AE","ä":"ae","Ö":"OE","ö":"oe","Ü":"UE","ü":"ue","ß":"ss","%":"prozent","&":"und","|":"oder","∑":"summe","∞":"unendlich","♥":"liebe"},"es":{"%":"por ciento","&":"y","<":"menor que",">":"mayor que","|":"o","¢":"centavos","£":"libras","¤":"moneda","₣":"francos","∑":"suma","∞":"infinito","♥":"amor"},"fr":{"%":"pourcent","&":"et","<":"plus petit",">":"plus grand","|":"ou","¢":"centime","£":"livre","¤":"devise","₣":"franc","∑":"somme","∞":"infini","♥":"amour"},"pt":{"%":"porcento","&":"e","<":"menor",">":"maior","|":"ou","¢":"centavo","∑":"soma","£":"libra","∞":"infinito","♥":"amor"},"uk":{"И":"Y","и":"y","Й":"Y","й":"y","Ц":"Ts","ц":"ts","Х":"Kh","х":"kh","Щ":"Shch","щ":"shch","Г":"H","г":"h"},"vi":{"Đ":"D","đ":"d"},"da":{"Ø":"OE","ø":"oe","Å":"AA","å":"aa","%":"procent","&":"og","|":"eller","$":"dollar","<":"mindre end",">":"større end"},"nb":{"&":"og","Å":"AA","Æ":"AE","Ø":"OE","å":"aa","æ":"ae","ø":"oe"},"it":{"&":"e"},"nl":{"&":"en"},"sv":{"&":"och","Å":"AA","Ä":"AE","Ö":"OE","å":"aa","ä":"ae","ö":"oe"}}');function o(u,f){if(typeof u!="string")throw new Error("slugify: string argument expected");f=typeof f=="string"?{replacement:f}:f||{};var h=a[f.locale]||{},g=f.replacement===void 0?"-":f.replacement,e=f.trim===void 0?!0:f.trim,i=u.normalize().split("").reduce(function(s,c){var l=h[c];return l===void 0&&(l=n[c]),l===void 0&&(l=c),l===g&&(l=" "),s+l.replace(f.remove||/[^\w\s$*_+~.()'"!\-:@]+/g,"")},"");return f.strict&&(i=i.replace(/[^A-Za-z0-9\s]/g,"")),e&&(i=i.trim()),i=i.replace(/\s+/g,g),f.lower&&(i=i.toLowerCase()),i}return o.extend=function(u){Object.assign(n,u)},o})})(ue);const ce=r=>r.split(/[\s-]/g).map(H).join(" ");function le(r,t){const{navigation:n}=P().public.content,a=u=>({...me(["title",...n.fields])(u),...ge(u==null?void 0:u.navigation)?u.navigation:{}}),o=r.sort((u,f)=>u._path.localeCompare(f._path)).reduce((u,f)=>{const h=f._path.substring(1).split("/"),g=f._id.split(":").slice(1),e=!!g[g.length-1].match(/([1-9][0-9]*\.)?index.md/g),i=l=>({title:l.title,_path:l._path,_file:l._file,children:[],...a(l),...l._draft?{_draft:!0}:{}}),s=i(f);if(e){const l=t[s._path];if(typeof(l==null?void 0:l.navigation)<"u"&&!(l!=null&&l.navigation))return u;if(f._path!=="/"){const m=i(f);s.children.push(m)}Object.assign(s,a(l))}return h.length===1?(u.push(s),u):(h.slice(0,-1).reduce((l,m,y)=>{const v="/"+h.slice(0,y+1).join("/"),w=t[v];if(typeof(w==null?void 0:w.navigation)<"u"&&!w.navigation)return[];let I=l.find(O=>O._path===v);return I||(I={title:ce(m),_path:v,_file:f._file,children:[],...a(w)},l.push(I)),I.children},u).push(s),u)},[]);return z(o)}const fe=new Intl.Collator(void 0,{numeric:!0,sensitivity:"base"});function z(r){var n;const t=r.sort((a,o)=>fe.compare(a._file,o._file));for(const a of t)(n=a.children)!=null&&n.length?z(a.children):delete a.children,delete a._file;return r}function me(r){return t=>(t=t||{},r&&r.length?r.filter(n=>typeof t[n]<"u").reduce((n,a)=>Object.assign(n,{[a]:t[a]}),{}):t)}function ge(r){return Object.prototype.toString.call(r)==="[object Object]"}const he=r=>U(r,P().public.content.api.baseURL),pe=ee(ie({driver:k()}),"@content");function de(r){async function t(){const n=new Set(await r.getKeys("cache:")),a=L().getPreviewToken();if(a){const u=await r.getItem(`${a}$`).then(g=>g||{});if(Array.isArray(u.ignoreSources)){const g=u.ignoreSources.map(e=>`cache:${e.trim()}:`);for(const e of n)g.some(i=>e.startsWith(i))&&n.delete(e)}const f=await r.getKeys(`${a}:`),h=await Promise.all(f.map(g=>r.getItem(g)));for(const g of h)n.delete(`cache:${g._id}`),g.__deleted||n.add(`${a}:${g._id}`)}return await Promise.all(Array.from(n).map(u=>r.getItem(u)))}return{storage:r,fetch:D(t),query:n=>J(D(t),n)}}let j=null,K=null;async function ye(){return K?await K:j||(K=we(),j=await K),j}async function we(){const r=Y(),{content:t}=P().public,n=de(pe),a=await n.storage.getItem("integrity");if(t.integrity!==+(a||0)){const{contents:o,navigation:u}=await $fetch(he(t.integrity?`cache.${t.integrity}.json`:"cache.json"));await Promise.all(o.map(f=>n.storage.setItem(`cache:${f._id}`,f))),await n.storage.setItem("navigation",u),await n.storage.setItem("integrity",t.integrity)}return await r.callHook("content:storage",n.storage),n}async function $e(r){const t=await ye();if(!L().getPreviewToken()&&Object.keys(r||{}).length===0)return t.storage.getItem("navigation");const n=await t.query(r).where({_partial:!1,navigation:{$ne:!1}}).find(),o=(await t.query().where({_path:/\/_dir$/i,_partial:!0}).find()).reduce((u,f)=>{var g;((g=f.title)==null?void 0:g.toLowerCase())==="dir"&&(f.title=void 0);const h=f._path.split("/").slice(0,-1).join("/")||"/";return u[h]={...f,...f.body},u},{});return le(n,o)}export{pe as contentStorage,de as createDB,$e as generateNavigation,ye as useContentDatabase};
