vec3 barycentric(in vec3 p1, in vec3 p2, in vec3 p3, in vec3 p0)
{
	vec3 a = p2 - p3;
	vec3 b = p1 - p3;
	vec3 c = p0 - p3;
	float ab = a.x * b.x + a.y * b.y + a.z * b.z;
	float ac = a.x * c.x + a.y * c.y + a.z * c.z;
	float bc = b.x * c.x + b.y * c.y + b.z * c.z;
	float m = a.x * a.x + a.y * a.y + a.z * a.z;
	float n = b.x * b.x + b.y * b.y + b.z * b.z;
	float d = m * n - ab * ab;
	float u = (m * bc - ab * ac) / d;
	float v = (n * ac - ab * bc) / d;
	float w = 1.0 - u - v;
    vec3 p = vec3(u,v,w);
    return ((p.x >= 0.0) && (p.x <= 1.0) && (p.y >= 0.0) && (p.y <= 1.0) && (p.z >= 0.0) && (p.z <= 1.0)) ? p : vec3(0.0);
}

void mainImage( out vec4 fragColor, in vec2 fragCoord )
{
  vec2 uv = (2.0 * fragCoord.xy / iResolution.xy - 1.0) * 2.0;   
	vec3 v0 = vec3(-1, -1, 0);
	vec3 v1 = vec3( 1, -1, 0);
	vec3 v2 = vec3( 0,  1, 0);	
	vec3 color = barycentric(v0, v1, v2, vec3(uv, 0.0));
	fragColor = vec4(color, 1.0);
}

