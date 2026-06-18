import { useEffect, useRef, useState } from 'react';
import { Layout, Menu, Card, Spin, Table, Typography, Space } from 'antd';
import { BarChartOutlined, PieChartOutlined, TableOutlined, FireOutlined } from '@ant-design/icons';
import * as echarts from 'echarts';
import axios from 'axios';
import 'antd/dist/reset.css';

const { Header, Content, Sider } = Layout;
const { Title, Text } = Typography;

const menuItems = [
  { key: 'score', icon: <BarChartOutlined />, label: '豆瓣评分分布' },
  { key: 'country', icon: <PieChartOutlined />, label: '豆瓣地区分布' },
  { key: 'movie', icon: <TableOutlined />, label: '豆瓣电影列表' },
  { key: 'hot', icon: <FireOutlined />, label: '百度热搜Top10' },
];

const movieColumns = [
  { title: '电影名', dataIndex: 'movie_name', key: 'movie_name' },
  { title: '评分', dataIndex: 'score', key: 'score' },
  { title: '导演', dataIndex: 'director', key: 'director' },
  { title: '主演', dataIndex: 'actors', key: 'actors' },
  { title: '年份', dataIndex: 'release_year', key: 'release_year' },
  { title: '地区', dataIndex: 'country', key: 'country' },
  { title: '类型', dataIndex: 'movie_type', key: 'movie_type' },
];

const hotColumns = [
  { title: '热搜标题', dataIndex: 'hot_title', key: 'hot_title' },
  { title: '热度', dataIndex: 'hot_score', key: 'hot_score' },
  {
    title: '链接',
    dataIndex: 'hot_url',
    key: 'hot_url',
    render: (text) => (
      <a href={text} target="_blank" rel="noreferrer">
        查看
      </a>
    ),
  },
];

function App() {
  const [selectedKey, setSelectedKey] = useState('score');
  const [loading, setLoading] = useState(false);
  const [chartData, setChartData] = useState([]);
  const [tableData, setTableData] = useState([]);
  const chartRef = useRef(null);
  const chartInstance = useRef(null);

  const fetchData = async (key) => {
    setLoading(true);
    try {
      let response;
      switch (key) {
        case 'score':
          response = await axios.get('/api/douban/stat/score');
          setChartData(response.data?.data || []);
          break;
        case 'country':
          response = await axios.get('/api/douban/stat/country');
          setChartData(response.data?.data || []);
          break;
        case 'movie':
          response = await axios.get('/api/douban/movie/list');
          setTableData(response.data?.data || []);
          break;
        case 'hot':
          response = await axios.get('/api/baidu/hot/list');
          setTableData(response.data?.data || []);
          break;
        default:
          break;
      }
    } catch (error) {
      console.error('接口请求失败：', error);
      setChartData([]);
      setTableData([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (!chartInstance.current && chartRef.current) {
      chartInstance.current = echarts.init(chartRef.current);
      window.addEventListener('resize', () => chartInstance.current?.resize());
    }
    return () => {
      window.removeEventListener('resize', () => chartInstance.current?.resize());
      chartInstance.current?.dispose();
    };
  }, []);

  useEffect(() => {
    fetchData(selectedKey);
  }, [selectedKey]);

  useEffect(() => {
    if (!chartInstance.current) return;
    if (selectedKey === 'score') {
      const xData = chartData.map((item) => item.score_range);
      const yData = chartData.map((item) => item.movie_count);
      chartInstance.current.setOption({
        title: { text: '豆瓣电影评分分布' },
        tooltip: { trigger: 'axis' },
        xAxis: { type: 'category', data: xData, axisLabel: { rotate: 0 } },
        yAxis: { type: 'value' },
        series: [
          {
            type: 'bar',
            data: yData,
            itemStyle: { color: '#1890ff' },
          },
        ],
      });
    } else if (selectedKey === 'country') {
      const pieData = chartData.map((item) => ({ name: item.country || '未知', value: item.movie_count }));
      chartInstance.current.setOption({
        title: { text: '豆瓣电影国家/地区分布' },
        tooltip: { trigger: 'item' },
        legend: { top: 'bottom' },
        series: [
          {
            type: 'pie',
            radius: ['40%', '70%'],
            avoidLabelOverlap: false,
            itemStyle: { borderRadius: 6, borderColor: '#fff', borderWidth: 2 },
            label: { show: false },
            emphasis: { label: { show: true, fontSize: '16', fontWeight: 'bold' } },
            data: pieData,
          },
        ],
      });
    }
  }, [selectedKey, chartData]);

  const renderContent = () => {
    if (loading) {
      return (
        <div className="content-loading">
          <Spin size="large" />
        </div>
      );
    }

    if (selectedKey === 'movie') {
      return <Table rowKey="id" columns={movieColumns} dataSource={tableData} pagination={{ pageSize: 10 }} />;
    }

    if (selectedKey === 'hot') {
      return <Table rowKey="id" columns={hotColumns} dataSource={tableData} pagination={false} />;
    }

    return <div ref={chartRef} className="chart-box" />;
  };

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider width={240} className="site-layout-background">
        <div className="logo">TE 数据可视化</div>
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[selectedKey]}
          items={menuItems}
          onClick={(item) => setSelectedKey(item.key)}
        />
      </Sider>
      <Layout>
        <Header className="header-bar">
          <Title level={3} style={{ color: '#fff', margin: 0 }}>
            后端数据可视化平台
          </Title>
        </Header>
        <Content className="content-container">
          <Card style={{ minHeight: 520 }}>
            <Space direction="vertical" size="large" style={{ width: '100%' }}>
              <Text type="secondary">当前视图：{menuItems.find((item) => item.key === selectedKey)?.label}</Text>
              {renderContent()}
            </Space>
          </Card>
        </Content>
      </Layout>
    </Layout>
  );
}

export default App;
