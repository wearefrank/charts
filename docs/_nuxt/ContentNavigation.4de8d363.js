import{q as f,e as v,j as g,u as d}from"./query.921812c6.js";import{O as l,R as h,j as _,S as y,m as C,M as w,C as P,Q as r}from"./entry.532d491b.js";import{h as p,u as $}from"./preview.809672a4.js";import{_ as j}from"./nuxt-link.79a32095.js";import{w as c,s as N,u as T}from"./utils.10201b9d.js";const D=async e=>{const{content:t}=l().public;typeof(e==null?void 0:e.params)!="function"&&(e=f(e));const a=e.params(),s=t.experimental.stripQueryParameters?c(`/navigation/${`${p(a)}.${t.integrity}`}/${v(a)}.json`):c(`/navigation/${p(a)}.${t.integrity}.json`);if(N())return(await h(()=>import("./client-db.c00a26e1.js"),["./client-db.c00a26e1.js","./entry.532d491b.js","./query.921812c6.js","./preview.809672a4.js","./utils.10201b9d.js","./index.a6ef77ff.js"],import.meta.url).then(o=>o.generateNavigation))(a);const n=await $fetch(s,{method:"GET",responseType:"json",params:t.experimental.stripQueryParameters?void 0:{_params:g(a),previewToken:$().getPreviewToken()}});if(typeof n=="string"&&n.startsWith("<!DOCTYPE html>"))throw new Error("Not found");return n},S=_({name:"ContentNavigation",props:{query:{type:Object,required:!1,default:void 0}},async setup(e){const{query:t}=y(e),a=C(()=>{var n;return typeof((n=t.value)==null?void 0:n.params)=="function"?t.value.params():t.value});if(!a.value&&w("dd-navigation").value){const{navigation:n}=T();return{navigation:n}}const{data:s}=await d(`content-navigation-${p(a.value)}`,()=>D(a.value));return{navigation:s}},render(e){const t=P(),{navigation:a}=e,s=o=>r(j,{to:o._path},()=>o.title),n=(o,u)=>r("ul",u?{"data-level":u}:null,o.map(i=>i.children?r("li",null,[s(i),n(i.children,u+1)]):r("li",null,s(i)))),m=o=>n(o,0);return t!=null&&t.default?t.default({navigation:a,...this.$attrs}):m(a)}});export{S as default};
