## 1.priority_queue定义

```cpp
template <class T, class Container = vector<T>,
  class Compare = less<typename Container::value_type> > class priority_queue;
12
```

- 按着这个模板定义来看，需要给出每一个**模板参数的类型**，来实例化模板。
  默认使用的是小于操作的比较运算符，底层使用vector来实现，算法使用make_heap,push_heap,pop_heap一系列堆操作来完成。

```cpp
//一个int 类型的优先队列，默认是越小越优先
priority_queue<int> que;
```

## 2.使用自定义的比较规则来初始化priority_queue

- 对于使用lambda函数作为模板参数的情况如下代码的说明部分。

```cpp
class student{
    public:
        int age;
        string name;
        /**重载小于操作符，
	      *这里必须是非成员函数才可以
		*/
        friend bool operator<(const student& a, const student & b){
            return a.age < b.age;
        }
};

/**可调用的函数操作符的对象*/
struct mycmp{
    bool operator()(const student & a,const student & b){
        return a.age < b.age;
    }
};

/**函数指针*/
bool cmpfunc(const student& a, const student& b){
    return a.age < b.age;
}

/**默认使用student的oprator<来进行比较*/
priority_queue<student> que1;

/**使用重载函数操作符的类对象*/
priority_queue<student,vector<student>,mycmp> que2;

/**定义一下比较函数*/
auto cmp = [](const student & a,const student & b){return a.age < b.age;};
/**
  *	需要把lambda表达式作为优先队列参数进行初始化
  * 并且指定priority_queue的模板实参，decltype(cmp)，c++11 declare type，声明类型
  * 可以认为是确定函数的类型
  * bool (const student & a,const student & b)
  **/
priority_queue<student,vector<student>,decltype(cmp)> que4(cmp);

/*使用函数对象来定义这个比较函数原型*/
//lambda 函数来初始化函数对象
priority_queue<student,vector<student>,function<bool(const student&,const student&)>> que5(cmp);

//函数指针来初始化函数对象
priority_queue<student,vector<student>,function<bool(const student&,const student&)>> que6(cmpfunc);

/**函数对象*/
function<bool(const student&,const student &)> func(cmpfunc);
priority_queue<student,vector<student>,function<bool(const student&,const student&)>> que7(func);

123456789101112131415161718192021222324252627282930313233343536373839404142434445464748495051
```

- 上述情况，也适用于其他的数据结构和算法。
- 例如：`lambda表达式`自定义函数算法，来进行结合`STL算法和数据结构`的使用。





# C++中priority_queue[优先级](https://so.csdn.net/so/search?q=优先级&spm=1001.2101.3001.7020)队列的初始化

优先级队列有3个可输入的参数

```cpp
priority_queue< type, container, function >
```

例如：

```cpp
priority_queue< int, vector<int>, less<int> > pq;
```

表示初始化一个[大顶堆](https://so.csdn.net/so/search?q=大顶堆&spm=1001.2101.3001.7020)pq，同时由于C++默认为大顶堆，因此在初始化大顶堆时，后两个参数可以省略，写做：

```cpp
priority_queue< int> pq;
```

小顶堆堆初始化为：

```cpp
priority_queue< int, vector<int>, greater<int> > pq;
```

当你需要进行自定义排序时，你可以构造一个自己的比较器：

```cpp
class Solution {
public:
    int fun(vector<int>& input) {
        priority_queue<int,vector<int>,cmp> pq;
        //dosomething
        return 0;
    }
    struct cmp{
        bool operator() (int a, int b ){ 
            //compare  
            return true; 
        }
    };
};
```

当你需要用已有数组对优先级队列进行初始化时：

```cpp
class Solution {
public:
    int fun(vector<int>& input) {
        priority_queue<int> pq(input.begin(),input.end());
        //dosomething
        return 0;
    }
};
```





# 构建注意事项

* **构建大顶堆cmp就用<**
* **构建小顶堆cmp就用>**

