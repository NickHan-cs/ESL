in array[3] in_pos;
out array[2] frag_pos;

void main() {
    gl_Position = {in_pos[0], in_pos[1], in_pos[2], 1};
    frag_pos = {gl_Position[0], gl_Position[1]};
}