#ifndef AVECTOR_H
#define AVECTOR_H

#include <initializer_list>

template <typename T>
class Array {
private:
	T* data;
	size_t length;
	size_t capacity;

public:
	Array() {
		data = nullptr;
		length = 0;
		capacity = 0;
	}

	Array(std::initializer_list<T> values) {
		length = values.size();
		capacity = length;

		data = new T[capacity];

		size_t i = 0;
		for (const T& value : values) {
			data[i] = value;
			i++;
		}
	}

	// Copy-Konstruktor
	Array(const Array& other) {
		length = other.length;
		capacity = other.capacity;

		if (capacity > 0) {
			data = new T[capacity];

			for (size_t i = 0; i < length; i++) {
				data[i] = other.data[i];
			}
		} else {
			data = nullptr;
		}
	}

	~Array() {
		delete[] data;
	}

	void push_back(const T& value) {
		if (length >= capacity) {
			size_t newCapacity = (capacity == 0) ? 4 : capacity * 2;

			T* newData = new T[newCapacity];

			for (size_t i = 0; i < length; i++) {
				newData[i] = data[i];
			}

			delete[] data;

			data = newData;
			capacity = newCapacity;
		}

		data[length] = value;
		length++;
	}

	size_t size() const {
		return length;
	}

	T& operator[](size_t index) {
		return data[index];
	}

	const T& operator[](size_t index) const {
		return data[index];
	}

	// Zuweisung: a = b
	Array& operator=(const Array& other) {
		if (this == &other)
			return *this;

		delete[] data;

		length = other.length;
		capacity = other.capacity;

		if (capacity > 0) {
			data = new T[capacity];

			for (size_t i = 0; i < length; i++) {
				data[i] = other.data[i];
			}
		} else {
			data = nullptr;
		}

		return *this;
	}

	// Vergleich: a == b
	bool operator==(const Array& other) const {
		if (length != other.length)
			return false;

		for (size_t i = 0; i < length; i++) {
			if (data[i] != other.data[i])
				return false;
		}

		return true;
	}

	// Vergleich: a != b
	bool operator!=(const Array& other) const {
		return !(*this == other);
	}
};

#endif
