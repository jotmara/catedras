const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:7045';
const fallback = [
 {codigo:'SED001',nombre:'Sede Central Medellín',direccion:'Calle 50 # 40-20',telefono:'6044440001'},
 {codigo:'SED002',nombre:'Sede San Benito',direccion:'Carrera 56 # 49-30',telefono:'6044440002'},
 {codigo:'SED003',nombre:'Sede Campus Universitario',direccion:'Avenida Colombia # 70-15',telefono:'6044440003'},
 {codigo:'SED004',nombre:'Sede Poblado',direccion:'Calle 10 # 43A-25',telefono:'6044440004'}
];
let offline = false;
async function request(path, options={}){const res=await fetch(`${API_BASE}${path}`,{headers:{'Content-Type':'application/json',...(options.headers||{})},...options});let body=null;try{body=await res.json()}catch{}if(!res.ok) throw new Error(body?.detalle||body?.mensaje||`Error HTTP ${res.status}`);return body}
export async function listSedes(){if(offline)return fallback;try{const data=await request('/api/sede');return data?.datos||[]}catch(e){offline=true;return fallback}}
export async function createSede(data){if(offline){fallback.push(data);return {estado:200}} return request('/api/sede',{method:'POST',body:JSON.stringify(data)})}
export async function updateSede(codigo,data){if(offline){const i=fallback.findIndex(x=>x.codigo===codigo);if(i>=0)fallback[i]={...fallback[i],...data};return {estado:200}} return request(`/api/sede/${codigo}`,{method:'PUT',body:JSON.stringify({nombre:data.nombre,direccion:data.direccion,telefono:data.telefono})})}
export async function deleteSede(codigo){if(offline){const i=fallback.findIndex(x=>x.codigo===codigo);if(i>=0)fallback.splice(i,1);return {estado:200}} return request(`/api/sede/${codigo}`,{method:'DELETE'})}
