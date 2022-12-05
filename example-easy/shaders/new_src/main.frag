in array[2] frag_pos;
out array[4] out_color;

array[3] barycentric(array[3] p1, array[3] p2, array[3] p3, array[3] p0)
{
    array[3] a, b, c, p, rlt;
    float ab, ac, bc, m, n, d, u, v, w;
    array[3] rlt = {0, 0, 0};
	a = p2 - p3;
	b = p1 - p3;
	c = p0 - p3;
	ab = a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
	ac = a[0] * c[0] + a[1] * c[1] + a[2] * c[2];
	bc = b[0] * c[0] + b[1] * c[1] + b[2] * c[2];
	m = a[0] * a[0] + a[1] * a[1] + a[2] * a[2];
	n = b[0] * b[0] + b[1] * b[1] + b[2] * b[2];
	d = m * n - ab * ab;
	u = (m * bc - ab * ac) / d;
	v = (n * ac - ab * bc) / d;
	w = 1 - u - v;
    p = {u, v, w};
    if (p[0] >= 0 && p[0] <= 1 && p[1] >= 0 && p[1] <= 1 && p[2] >= 0 && p[2] <= 1) {
        rlt = p;
    }
    return rlt;
}

array[4] mainImage(array[2] fragCoord) {
    array[4] fragColor;
    array[2] uv;
    array[3] color, tmp;
    array[3] v0 = {-1, -1, 0};
    array[3] v1 = {1, -1, 0};
    array[3] v2 = {0, 1, 0};
    uv = (2 * fragCoord / iResolution - 1.0) * 2.0;
    tmp = {uv[0], uv[1], 0};
	color = barycentric(v0, v1, v2, tmp);
    fragColor = {color[0], color[1], color[2], 1};
	return fragColor;
}

void main() {
    array[2] fragCoord;
    array[4] uFragColor = {0, 0, 0, 0};
    fragCoord = {gl_FragCoord[0], gl_FragCoord[1]};
    fragCoord[1] = iResolution[1] - fragCoord[1];
    out_color = mainImage(fragCoord);
}