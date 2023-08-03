#include <iostream>
#include <string>
#include <cmath>
#include <chrono>
#include <cstdlib>

using namespace std;

string bin_hex(string s)//2->16
{
	string hex = "";
	int tmp = 0;
	while (s.size() % 4 != 0)
		s = "0" + s;
	for (int i = 0; i < s.size(); i += 4)
	{
		tmp = (s[i] - '0') * 8 + (s[i + 1] - '0') * 4 + (s[i + 2] - '0') * 2 + (s[i + 3] - '0') * 1;
		if (tmp < 10)
			hex += to_string(tmp);
		else
			hex += 'A' + (tmp - 10);
	}
	return hex;
}

string hex_bin(string s)//16->2
{
	string bin = "";
	string table[16] = {
	"0000","0001","0010","0011",
	"0100","0101","0110","0111",
	"1000","1001","1010","1011",
	"1100","1101","1110","1111" };
	for (int i = 0; i < s.size(); i++)
	{
		if (s[i] >= 'A' && s[i] <= 'F')
			bin += table[s[i] - 'A' + 10];
		else
			bin += table[s[i] - '0'];
	}
	return bin;
}

int bin_dec(string s) {
	int dec = 0;
	for (int i = 0; i < s.size(); i++) {
		dec += (s[i] - '0') * pow(2, s.size() - i - 1);
	}
	return dec;
}

string dec_bin(int s)
{
	string bin = "";
	while (s >= 1) {
		bin = to_string(s % 2) + bin;
		s = s / 2;
	}
	return bin;
}

int hex_dec(string s)
{
	int dec = 0;
	for (int i = 0; i < s.size(); i++)
	{
		if (s[i] >= 'A' && s[i] <= 'F')
			dec += (s[i] - 'A' + 10) * pow(16, s.size() - i - 1);
		else
			dec += (s[i] - '0') * pow(16, s.size() - i - 1);
	}
	return dec;
}

string dec_hex(int s)
{
	string hex = "";
	int temp = 0;
	while (s >= 1)
	{
		temp = s % 16;
		if (temp < 10 && temp >= 0)
			hex = to_string(temp) + hex;
		else
			hex += ('A' + (temp - 10));
		s = s / 16;
	}
	return hex;
}

string leftshift(string s, int len)
{
	string r = hex_bin(s);
	r = r.substr(len) + r.substr(0, len);
	return bin_hex(r);
}

string XOR(string s1, string s2)
{
	string r1 = hex_bin(s1);
	string r2 = hex_bin(s2);
	string r = "";
	for (int i = 0; i < r1.size(); i++)
	{
		if (r1[i] == r2[i])
			r += "0";
		else
			r += "1";
	}
	return bin_hex(r);
}

string AND(string s1, string s2)
{
	string r1 = hex_bin(s1);
	string r2 = hex_bin(s2);
	string r = "";
	for (int i = 0; i < r1.size(); i++)
	{
		if (r1[i] == '1' && r2[i] == '1')
			r += "1";
		else
			r += "0";
	}
	return bin_hex(r);
}

string OR(string s1, string s2)
{
	string r1 = hex_bin(s1);
	string r2 = hex_bin(s2);
	string r = "";
	for (int i = 0; i < r1.size(); i++)
	{
		if (r1[i] == '0' && r2[i] == '0')
			r += "0";
		else
			r += "1";
	}
	return bin_hex(r);
}

string NOT(string s)
{
	string r1 = hex_bin(s);
	string r = "";
	for (int i = 0; i < r1.size(); i++)
	{
		if (r1[i] == '0')
			r += "1";
		else
			r += "0";
	}
	return bin_hex(r);
}

char Xor(char s1, char s2)
{
	return s1 == s2 ? '0' : '1';
}

char And(char s1, char s2)
{
	return (s1 == '1' && s2 == '1') ? '1' : '0';
}

string add_mod(string s1, string s2)
{
	string r1 = hex_bin(s1);
	string r2 = hex_bin(s2);
	string r = "";
	char tmp = '0';
	for (int i = r1.size() - 1; i >= 0; i--)
	{
		r = Xor(Xor(r1[i], r2[i]), tmp) + r;
		if (And(r1[i], r2[i]) == '1')
			tmp = '1';
		else
		{
			if (Xor(r1[i], r2[i]) == '1')
				tmp = And('1', tmp);
			else
				tmp = '0';
		}
	}
	return bin_hex(r);
}

string padding(string s)
{
	string r = "";
	for (int i = 0; i < s.size(); i++)
		r += dec_hex((int)s[i]);
	
	int length = r.size() * 4;
	r += "8";
	while (r.size() % 128 != 112)
		r += "0";

	string len = dec_hex(length);
	while (len.size() != 16)
		len = "0" + len;

	r += len;
	return r;
}

string P0(string s)
{
	return XOR(XOR(s, leftshift(s, 9)), leftshift(s, 17));
}

string P1(string s)
{
	return XOR(XOR(s, leftshift(s, 15)), leftshift(s, 23));
}

string T(int i)
{
	if (0 <= i && i <= 15)
		return "79CC4519";
	else
		return "7A879D8A";
}

string FF(string s1, string s2, string s3, int i)
{
	if (0 <= i && i <= 15)
		return XOR(XOR(s1, s2), s3);
	else
		return OR(OR(AND(s1, s2), AND(s1, s3)), AND(s2, s3));
}

string GG(string s1, string s2, string s3, int i) {//实现布尔函数GG功能
	if (0 <= i && i <= 15)
		return XOR(XOR(s1, s2), s3);
	else
		return OR(AND(s1, s2), AND(NOT(s1), s3));
}

string message_extension(string s)
{
	string r = s;
	for (int i = 16; i < 68; i++) //17至68位
		r += XOR(XOR(P1(XOR(XOR(r.substr((i - 16) * 8, 8), r.substr((i - 9) * 8, 8)), leftshift(r.substr((i - 3) * 8, 8), 15))), leftshift(r.substr((i - 13) * 8, 8), 7)), r.substr((i - 6) * 8, 8));
	
	for (int i = 0; i < 64; i++)
		r += XOR(r.substr(i * 8, 8), r.substr((i + 4) * 8, 8));
	
	return r;
}

string message_compress(string s1, string s2)
{
	string iv = s2;
	string a = iv.substr(0, 8), b = iv.substr(8, 8), c = iv.substr(16, 8), d = iv.substr(24, 8);
	string e = iv.substr(32, 8), f = iv.substr(40, 8), g = iv.substr(48, 8), h = iv.substr(56, 8);
	string ss1 = "", ss2 = "";
	string tt1 = "", tt2 = "";
	
	for (int i = 0; i < 64; i++)
	{
		ss1 = leftshift(add_mod(add_mod(leftshift(a, 12), e), leftshift(T(i), (i % 32))), 7);
		ss2 = XOR(ss1, leftshift(a, 12));
		tt1 = add_mod(add_mod(add_mod(FF(a, b, c, i), d), ss2), s1.substr((i + 68) * 8, 8));
		tt2 = add_mod(add_mod(add_mod(GG(e, f, g, i), h), ss1), s1.substr(i * 8, 8));
		d = c;
		c = leftshift(b, 9);
		b = a;
		a = tt1;
		h = g;
		g = leftshift(f, 19);
		f = e;
		e = P0(tt2);
	}
	return (a + b + c + d + e + f + g + h);
}

string iteration_compress(string s)
{
	int n = s.size() / 128;
	string iv = "7380166F4914B2B9172442D7DA8A0600A96F30BC163138AAE38DEE4DB0FB0E4E";
	string m = "", em = "", cm = "";
	for (int i = 0; i < n; i++)
	{
		m = s.substr(i * 128, 128);
		em = message_extension(m);
		cm = message_compress(em, iv);
		iv = XOR(iv, cm);
	}
	return iv;
}

int main()
{
	string s = "20220430";
	auto start = std::chrono::steady_clock::now();
	string tmp = padding(s);
	string r = iteration_compress(tmp);
	auto end = std::chrono::steady_clock::now();
	double t = std::chrono::duration<double, std::milli>(end - start).count();
	printf("Time：%.2fms", t);
}

