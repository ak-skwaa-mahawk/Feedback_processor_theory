float R_neighbor = ((float)buf[0]) / 255.0f;
memcpy(glyph_data, buf + 1, 64);
float R_local = calc_resonance(glyph_data, glyph_data);
mesh_coherence = fminf(R_local, R_neighbor);
