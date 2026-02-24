class Arithmetic_Coding():

    BITS = 32
    MAX = 1 << BITS
    HALF = MAX >> 1
    QUARTER = HALF >> 1
    THREE_QUARTER = QUARTER * 3
    
    def __init__(self):
        self.low = 0
        self.high = Arithmetic_Coding.MAX

class Arithmetic_Encoding(Arithmetic_Coding):
    
    def __init__(self):
        super().__init__()
        self.pending_bits = 0

    def _emit_bit(self, output, bit, pending):
        output.append(bit)
        if pending:
            output.extend([not bit] * pending)

    def encode_symbol(self, symbol, model, output):
        s_low, s_high, total_freq = model.get_range(symbol)
        range_ = self.high - self.low
        self.high = self.low + (range_ * s_high) // total_freq
        self.low  = self.low + (range_ * s_low)  // total_freq

        while True:
            if self.high <= Arithmetic_Coding.HALF:
                self._emit_bit(output, 0, self.pending_bits)
                self.pending_bits = 0
            elif self.low >= Arithmetic_Coding.HALF:
                self._emit_bit(output, 1, self.pending_bits)
                self.pending_bits = 0
                self.low -= Arithmetic_Coding.HALF
                self.high -= Arithmetic_Coding.HALF
            elif self.low >= Arithmetic_Coding.QUARTER and self.high <= Arithmetic_Coding.THREE_QUARTER:
                self.pending_bits += 1
                self.low -= Arithmetic_Coding.QUARTER
                self.high -= Arithmetic_Coding.QUARTER
            else:
                break
            self.low *= 2
            self.high *= 2

    def flush(self, output):
        self.pending_bits += 1
        if self.low < Arithmetic_Coding.QUARTER:
            self._emit_bit(output, 0, self.pending_bits)
        else:
            self._emit_bit(output, 1, self.pending_bits)

class Arithmetic_Decoding(Arithmetic_Coding):
    
    def __init__(self):
        super().__init__()

    def start(self, bits):
        bit_list = bits.tolist()
        self.bit_iter = iter(bit_list)
        self.value = 0
        for _ in range(Arithmetic_Coding.BITS):
            self.value <<= 1
            if next(self.bit_iter, 0): self.value |= 1

    def decode_symbol(self, model):
        total_freq = model.total
        range_ = self.high - self.low
        offset = self.value - self.low
        scaled_value = ((offset + 1) * total_freq - 1) // range_
        if scaled_value >= total_freq: scaled_value = total_freq - 1
        symbol, s_low, s_high = model.get_symbol_from_scaled_value(scaled_value)        
        self.high = self.low + (range_ * s_high) // total_freq
        self.low  = self.low + (range_ * s_low)  // total_freq
        while True:
            if self.high <= Arithmetic_Coding.HALF:
                pass
            elif self.low >= Arithmetic_Coding.HALF:
                self.low -= Arithmetic_Coding.HALF
                self.high -= Arithmetic_Coding.HALF
                self.value -= Arithmetic_Coding.HALF
            elif self.low >= Arithmetic_Coding.QUARTER and self.high <= Arithmetic_Coding.THREE_QUARTER:
                self.low -= Arithmetic_Coding.QUARTER
                self.high -= Arithmetic_Coding.QUARTER
                self.value -= Arithmetic_Coding.QUARTER
            else:
                break
            self.low += self.low
            self.high += self.high
            self.value += self.value
            try:
                if next(self.bit_iter): self.value |= 1
            except StopIteration: pass
        return symbol
