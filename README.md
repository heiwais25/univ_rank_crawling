## University rank crawling
This package is used for crawling of university rank. The current web page is https://www.topuniversities.com/. From this page, it will read ranking under the various condition. The rank information will be stored in **json** format to be used by other program. For now, rank information obtained in 2018 is used.

### Requirements
- Driver
	- PhantomJS : It is used by selenium

- Phython package
	- selenium
	- bs4

### Output format
In the json file, the main categories are **univ_info** and **rank**.

- `univ_info` : It includes name and country of each university.
- `rank` : It consists of rank information obtained under each country and subject condition. In the each rank, the indices of university corresponding to the **univ_info** list are stored. By using this index, we can get university information easily.
 

<p align="center">
	<img src="./img/json_format_desc.png" alt="format_desc" width="600"/>
</p>
<!-- ![format_desc](./img/json_format_desc.png | width=600)  -->