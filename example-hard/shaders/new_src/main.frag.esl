in array[2] frag_pos;
out array[4] out_color;

float br, tub, hit;
array[3] pos, sphpos;
float det = 0.001;

array[3][3] lookat(array[3] dir, array[3] up) {
    array[3] rt, tmp;
    array[3][3] rlt;
    tmp = cross(dir, up);
    rt = normalize(tmp);
    tmp = cross(rt, dir);
    rlt = {{rt[0], rt[1], rt[2]}, {tmp[0], tmp[1], tmp[2]}, {dir[0], dir[1], dir[2]}};
    return rlt;
}

array[3] path(float t) {
    array[3] rlt;
    rlt = {sin(t + cos(t) * 0.5) * 0.5, cos(t * 0.5), t};
    return rlt;
}

array[2][2] rot(float a) {
    float s, c;
    array[2][2] rlt;
    s = sin(a);
    c = sin(a);
    rlt = {{c, s}, {-s, c}};
    return rlt;
}

array[3] fractal(array[2] p) {
    float m = 1000;
    float i = 0;
    array[3] tmp;
    p = fract(p * 0.1);
    while (i < 7) {
        p = abs(p) / clamp(abs(p[0] * p[1]), 0.25, 2) - 1.2;
        m = min(m, abs(p[1]) + fract(p[0] * 0.3 + iTime * 0.5 + i * 0.25));
        i = i + 1;
    }
    m = exp(-6 * m);
    tmp = {abs(p[0]), m, abs(p[1])};
    return m * tmp;
}

float coso(array[3] pp) {
    array[2] tmp;
    float sph, br2;
    pp = pp * 0.7;

    tmp = {pp[0], pp[1]};
    tmp = tmp * rot(pp[2] * 2);
    pp[0] = tmp[0];
    pp[1] = tmp[1];

    tmp[1] = pp[2];
    tmp = tmp * rot(iTime * 2);
    pp[0] = tmp[0];
    pp[2] = tmp[1];

    tmp[0] = pp[1];
    tmp = tmp * rot(iTime);
    pp[1] = tmp[0];
    pp[2] = tmp[1];

    sph = length(pp) - 0.04;
    sph = sph - length(sin(pp * 40)) * 0.05;
    sph = max(sph, -length(pp) + 0.11);
    br2 = length(pp) - 0.03;

    tmp = {pp[0], pp[1]};
    br2 = min(br2, length(tmp) + 0.005);
    tmp = {pp[0], pp[2]};
    br2 = min(br2, length(tmp) + 0.005);
    tmp = {pp[1], pp[2]};
    br2 = min(br2, length(tmp) + 0.005);
    br2 = max(br2, length(pp) - 1);
    br = min(br2, br);
    return min(br, sph);
}

float de(array[3] p) {
    array[3] pp, tmp2;
    array[2] tmp1, tmp3;
    float s, co, d;
    int i = 0;
    hit = 0;
    br = 1000;
    pp = p - sphpos;

    tmp1 = {p[0], p[1]};
    tmp2 = path(p[2]);
    tmp3 = {tmp2[0], tmp2[1]};

    tmp1 = tmp1 - tmp3;
    tmp1 = tmp1 * rot(p[2] + iTime * 0.5);

    s = sin(p[2] * 0.5 + iTime * 0.5);
    tmp1 = tmp1 * (1.3 - s * s * 0.7);
    p[0] = tmp1[0];
    p[1] = tmp1[1];

    while (i < 6) {
        p = abs(p) - 0.4;
        i = i + 1;
    }
    pos = p;
    tmp1 = {p[0], p[1]};
    tub = -length(tmp1) + 0.45 + sin(p[2] * 10) * 0.1 * smoothstep(0.4, 0.5, abs(0.5 - fract(p[2] * 0.05)) * 2);
    co = coso(pp);
    co = min(co, coso(pp + 0.7));
    co = min(co, coso(pp - 0.7));
    d = min(tub, co);
    if (d == tub) {
        hit = step(fract(0.1 * length(sin(p * 10))), 0.05);
    }
    return d * 0.3;
}

array[3] march(array[3] from, array[3] dir) {
    array[2] uv, tmp1;
    array[3] col, p, n, tmp2;
    float d, td, g, ref, ltd, li, f;
    array[2] e = {0, 0.1};
    array[3] e_yxx = {0.1, 0, 0};
    array[3] e_xyx = {0, 0.1, 0};
    array[3] e_xxy = {0, 0, 0.1};
    array[3] tmp3 = {0.2, 0.1, 0.5};
    array[3] tmp4 = {2, 1, 2};
    array[3] tmp5 = {0.8, 0.7, 0.7};
    array[3] tmp6 = {1, 1, 1};
    int i = 0;
    tmp1 = {dir[0], dir[1]};
    uv = {atan(dir[0], dir[1]) + iTime * 0.5, length(tmp1) + sin(iTime * 0.2)};
    col = fractal(uv);
    p = from;
    while (i < 200) {
        p = p + dir * d;
        d = de(p);
        if (d < det && ref == 0 && hit == 1) {
            tmp2 = {de(p + e_yxx), de(p + e_xyx), de(p + e_xxy)};
            n = normalize(tmp2 - de(p));
            p = p - dir * d * 2;
            dir = reflect(dir, n);
            ref = 1;
            td = 0;
            ltd = td;
        } else {
            if (d < det || td > 5) {
                break;
            }
            td = td + d;
            g = g + 0.1 / (0.1 + br * 13);
            li = li + 0.1 / (0.1 + tub * 5);
        }
        i = i + 1;
    }
    g = max(g, li * 0.15);
    f = 1 - td / 3;
    if (ref == 1) {
        f = 1 - ltd / 3;
    }
    if (d < 0.01) {
        col = {1, 1, 1};
        e = {0, det};
        e_yxx = {det, 0, 0};
        e_xyx = {0, det, 0};
        e_xxy = {0, 0, det};
        tmp2 = {de(p + e_yxx), de(p + e_xyx), de(p + e_xxy)};
        n = normalize(tmp2 - de(p));
        tmp2 = {tmp2[0], tmp2[0], tmp2[0]};
        col = tmp2 * 0.7;
        col = col + fract(pos[2] * 5) * tmp3;
        tmp1 = {pos[0], pos[2]};
        col = col + fractal(tmp1 * 2);
        if (tub > 0.01) {
            col = {0, 0, 0};
        }
    }
    col = col * f;
    glo = g * 0.1 * tmp4 * (0.5 + fract(sin(iTime) * 123.456) * 1.5) * 0.5;
    tmp1 = {glo[0], glo[2]};
    tmp1 = tmp1 * rot(dir[1] * 1.5);
    col = col + glo;
    col = col * tmp5;
    col = mix(col, tmp6, ref * 0.3);
    return col;
}

array[4] mainImage(array[2] fragCoord) {
    array[2] uv, tmp1;
    array[3] from, fw, col, tmp2;
    array[4] rlt;
    float t;
    array[3] tmp3 = {0.5, 0.5, 0.5};
    uv = {gl_FragCoord[0] / iResolution[0], gl_FragCoord[1] / iResolution[1]};
    uv = uv - 0.5;
    tmp1 = {iResolution[1] / iResolution[0], 1};
    uv = uv / tmp1;
    t = iTime;
    from = path(t);
    if (mod(iTime, 10) > 5) {
        from = path(floor(t / 4 + 0.5) * 4);
    }
    sphpos = path(t + 0.5);
    from[0] = from[0] + 0.2;
    fw = normalize(path(t + 0.5) - from);
    tmp2 = {uv[0], uv[1], 0.5};
    dir = normalize(tmp2);
    tmp2 = {fw[0] * 2, 1, 0};
    dir = lookat(fw, tmp2) * dir;
    tmp1 = {dir[0], dir[2]};
    tmp1 = tmp1 + sin(iTime * 0.3);
    dir[0] = tmp1[0];
    dir[2] = tmp1[1];
    col = march(from, dir);
    col = mix(tmp3 * length(col), col, 0.8);
    rlt = {col[0], col[1], col[2], 1};
    return rlt;
}

void main() {
    array[4] uFragColor = {0, 0, 0, 0};
    array[2] fragCoord;
    fragCoord = {gl_FragCoord[0], gl_FragCoord[1]};
    fragCoord[1] = iResolution[1] - fragCoord[1];
    out_color = mainImage(fragCoord);
}