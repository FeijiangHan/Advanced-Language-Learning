# map的使用



```cpp
template < class Key,                                   //map::key_tpe
           class T,                                     //map::mapped_type
           class Compare = less<Key>,                   //map::key_compare
           class Alloc = allocator<pair<const Key, T>>  //map::allocator_type
           > class map;
```

1. 第一个参数存储了key值

2. 第二个参数存储了value值

3. 第三个参数是比较函数的类对象，用它来判断两个key值大小，并返回bool类型结果。默认值是less<Key>。定义如下:

   ```cpp
   template <class T> 
   
   
   
   struct less {
   
   
   
     bool operator() (const T& x, const T& y) const {return x < y;}
   
   
   
     typedef T first_argument_type;
   
   
   
     typedef T second_argument_type;
   
   
   
     typedef bool result_type;
   
   
   
   };
   ```

4. 第四个参数是用来定义map的内存分配器

由此可以看出，自定义key值比较肯定与第三个参数有关。

1.对less<key>模板类进行特化，特化为绝对类型

```cpp
#include <iostream>



#include <map>



#include <string>



 



using namespace std;



 



class Stone {



public:



	Stone() = default;



	Stone(string name, int weight) :m_name(name), m_weight(weight) {}



 



	string m_name;



	int m_weight;



};



 



 



template<>



struct less<Stone> {



public:



	// 函数const限定修饰符一定不要丢，必须和less<Key> 模板类保持一致



	bool operator()(const Stone& t1, const Stone& t2) const {



		cout << "less<Stone> is called" << endl;



		if (t1.m_weight == t2.m_weight)



		{



			return t1.m_name.length() < t2.m_name.length();



		}



		return t1.m_weight < t2.m_weight;



	}



};



 



int main(int argc, char** argv)



{



	map<Stone, size_t> stones;



	stones[Stone("Jade", 888)] = 1;



	stones[Stone("CommonStone", 22)] = 3;



	stones[Stone("Griotte", 66)] = 5;



 



	for (auto& iter : stones)



	{



		cout << iter.first.m_name << ","



			<< iter.first.m_weight << ","



			<< iter.second << endl;



	}



	return 0;



}
```

2.利用仿函数功能std::function,可以对任何可调用的目标实体（包括普通函数、Lambda表达式、函数指针、类静态函数以及其他函数对象等）进行安全封装。

```cpp
#include <iostream>



#include <map>



#include <string>



#include <functional>



 



using namespace std;



 



class Stone {



public:



	Stone() = default;



	Stone(string name, int weight) :m_name(name), m_weight(weight) {}



 



	string m_name;



	int m_weight;



};



 



bool Compare(const Stone& t1, const Stone& t2)



{



	cout << " funciton Compare is called" << endl;



	if (t1.m_weight == t2.m_weight)



	{



		return t1.m_name.length() < t2.m_name.length();



	}



	return t1.m_weight < t2.m_weight;



}



 



int main(int argc, char** argv)



{



	map < Stone, size_t, std::function<bool(const Stone& t1, const Stone& t2)> > stones(Compare);



	stones[Stone("Jade", 888)] = 1;



	stones[Stone("CommonStone", 22)] = 3;



	stones[Stone("Griotte", 66)] = 5;



 



	for (auto& iter : stones)



	{



		cout << iter.first.m_name << ","



			<< iter.first.m_weight << ","



			<< iter.second << endl;



	}



	return 0;



}
```

3.最简单的方法，将less<key>模板类示例化，重载operator()函数

```cpp
#include <iostream>



#include <map>



#include <string>



 



 



using namespace std;



 



class Stone {



public:



	Stone() = default;



	Stone(string name, int weight) :m_name(name), m_weight(weight) {}



 



	string m_name;



	int m_weight;



};



 



struct CompareClass {



public:



	// 函数const限定修饰符一定不要丢，必须和less<Key> 模板类保持一致



	bool operator()(const Stone& t1, const Stone& t2) const {



		cout << "CompareClass is called" << endl;



		if (t1.m_weight == t2.m_weight)



		{



			return t1.m_name.length() < t2.m_name.length();



		}



		return t1.m_weight < t2.m_weight;



	}



};



 



int main(int argc, char** argv)



{



	map < Stone, size_t,  CompareClass> stones;



	stones[Stone("Jade", 888)] = 1;



	stones[Stone("CommonStone", 22)] = 3;



	stones[Stone("Griotte", 66)] = 5;



 



	for (auto& iter : stones)



	{



		cout << iter.first.m_name << ","



			<< iter.first.m_weight << ","



			<< iter.second << endl;



	}



	return 0;



}
```



当然，还有最最最简单的方法——在自定义对象中重载operator<()运算符

c++11标准里，比较两个对象肯定要用到operator<()运算符，我们直接重载它就可以进行比较

```cpp
#include <iostream>



#include <map>



#include <string>



 



using namespace std;



 



class Stone {



public:



	Stone() = default;



	Stone(string name, int weight) :m_name(name), m_weight(weight) {}



 



	string m_name;



	int m_weight;



	bool operator<(const Stone& lvalue) const 



	{



		cout << "operator<() is called" << endl;



		if (this->m_weight == lvalue.m_weight)



		{



			return this->m_name.length() < lvalue.m_name.length();



		}



		return this->m_weight < lvalue.m_weight;



	}



};



 



int main(int argc, char** argv)



{



	map < Stone, size_t> stones;



	stones[Stone("Jade", 888)] = 1;



	stones[Stone("CommonStone", 22)] = 3;



	stones[Stone("Griotte", 66)] = 5;



 



	for (auto& iter : stones)



	{



		cout << iter.first.m_name << ","



			<< iter.first.m_weight << ","



			<< iter.second << endl;



	}



	return 0;



}
```